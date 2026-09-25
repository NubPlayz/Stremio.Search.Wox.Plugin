import os
import sys
import asyncio
import webbrowser
from typing import List, Optional

# main.py lives in a package, so climb one level to reach the plugin root.
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
deps_dir = os.path.join(base_dir, "dependencies")
if os.path.isdir(deps_dir) and deps_dir not in sys.path:
    sys.path.insert(0, deps_dir)

from wox_plugin import (
    ActionContext,
    ChangeQueryParam,
    Context,
    CopyParams,
    CopyType,
    LogLevel,
    Plugin,
    PluginInitParams,
    PublicAPI,
    Query,
    QueryResponse,
    QueryType,
    RefreshQueryParam,
    Result,
    ResultAction,
    WoxImage,
)

from plugin.stremio_search import (
    handle_query,
    refresh_library,
    StremioMediaItem,
    StremioInfoItem,
    StremioSearchResult,
)


class StremioSearchPlugin(Plugin):
    api: PublicAPI
    power_user_mode: bool = False

    async def init(self, ctx: Context, init_params: PluginInitParams) -> None:
        self.api = init_params.api
        try:
            val = await self.api.get_setting(ctx, "require_question_mark_for_online")
            self.power_user_mode = str(val).lower() in ("true", "1", "yes")
        except Exception:
            self.power_user_mode = False

        try:
            await self.api.on_setting_changed(ctx, self._on_setting_changed)
        except Exception as e:
            await self.api.log(ctx, LogLevel.WARNING, f"Failed registering on_setting_changed: {e}")

    async def _on_setting_changed(self, ctx: Context, key: str, value: str) -> None:
        if key == "require_question_mark_for_online":
            self.power_user_mode = str(value).lower() in ("true", "1", "yes")

    async def action_open_url(self, ctx: Context, action_ctx: ActionContext) -> None:
        url = action_ctx.context_data.get("url")
        if url:
            try:
                webbrowser.open(url)
            except Exception as e:
                await self.api.log(ctx, LogLevel.ERROR, f"Failed opening url {url}: {e}")

    async def action_sync_library(self, ctx: Context, action_ctx: ActionContext) -> None:
        success, msg = refresh_library()
        try:
            await self.api.notify(ctx, msg)
            await self.api.refresh_query(ctx, RefreshQueryParam(preserve_selected_index=False))
        except Exception as e:
            await self.api.log(ctx, LogLevel.ERROR, f"Failed notifying library sync: {e}")

    async def action_change_query(self, ctx: Context, action_ctx: ActionContext) -> None:
        query_text = action_ctx.context_data.get("query_text", "")
        if query_text:
            try:
                await self.api.change_query(
                    ctx,
                    ChangeQueryParam(query_type=QueryType.INPUT, query_text=query_text),
                )
            except Exception as e:
                await self.api.log(ctx, LogLevel.ERROR, f"Failed changing query: {e}")

    async def action_copy_text(self, ctx: Context, action_ctx: ActionContext) -> None:
        text = action_ctx.context_data.get("text", "")
        if text:
            try:
                await self.api.copy(ctx, CopyParams(type=CopyType.TEXT, text=text))
                await self.api.notify(ctx, "Link copied to clipboard")
            except Exception as e:
                await self.api.log(ctx, LogLevel.ERROR, f"Failed copying to clipboard: {e}")

    def _convert_media_item(self, item: StremioMediaItem) -> Result:
        if item.poster_url:
            icon = WoxImage.new_url(item.poster_url)
        else:
            icon = WoxImage.new_relative(item.icon_fallback)

        actions = [
            ResultAction(
                name="Open in Stremio Desktop",
                icon=WoxImage.new_relative("assets/icon.png"),
                is_default=True,
                context_data={"url": item.deeplink},
                action=self.action_open_url,
            ),
            ResultAction(
                name="Open in Web Browser",
                icon=WoxImage.new_relative("assets/icon.png"),
                context_data={"url": item.weblink},
                action=self.action_open_url,
            ),
            ResultAction(
                name="Sync Stremio Library",
                icon=WoxImage.new_relative("assets/icon.png"),
                action=self.action_sync_library,
            ),
            ResultAction(
                name="Copy Stremio Link",
                icon=WoxImage.new_relative("assets/icon.png"),
                context_data={"text": item.deeplink},
                action=self.action_copy_text,
            ),
            ResultAction(
                name="Copy Web Link",
                icon=WoxImage.new_relative("assets/icon.png"),
                context_data={"text": item.weblink},
                action=self.action_copy_text,
            ),
            ResultAction(
                name="Support this plugin by starring it!",
                icon=WoxImage.new_relative("assets/icon.png"),
                context_data={"url": "https://github.com/NubPlayz/Stremio.Search.Wox.Plugin"},
                action=self.action_open_url,
            ),
        ]

        return Result(
            id=item.id,
            title=item.title,
            sub_title=item.sub_title,
            icon=icon,
            score=item.score,
            actions=actions,
        )

    def _convert_info_item(self, item: StremioInfoItem) -> Result:
        icon = WoxImage.new_relative(item.icon)
        actions = []

        if item.kind == "sync_prompt":
            actions.append(
                ResultAction(
                    name="Sync Stremio Library Now",
                    icon=icon,
                    is_default=True,
                    action=self.action_sync_library,
                )
            )
            actions.append(
                ResultAction(
                    name="Support this plugin by starring it!",
                    icon=icon,
                    context_data={"url": "https://github.com/NubPlayz/Stremio.Search.Wox.Plugin"},
                    action=self.action_open_url,
                )
            )
        elif item.kind == "query_hint":
            actions.append(
                ResultAction(
                    name="Append '?' to search online catalog",
                    icon=icon,
                    is_default=True,
                    prevent_hide_after_action=True,
                    context_data={"query_text": item.target_query},
                    action=self.action_change_query,
                )
            )

        return Result(
            id=item.id,
            title=item.title,
            sub_title=item.sub_title,
            icon=icon,
            actions=actions,
        )

    async def query(self, ctx: Context, query: Query) -> QueryResponse:
        search_term = query.search or ""
        domain_items = await asyncio.to_thread(
            handle_query, search_term, power_user_mode=self.power_user_mode
        )

        wox_results: List[Result] = []
        for item in domain_items:
            if isinstance(item, StremioMediaItem):
                wox_results.append(self._convert_media_item(item))
            elif isinstance(item, StremioInfoItem):
                wox_results.append(self._convert_info_item(item))

        return QueryResponse(results=wox_results)



plugin = StremioSearchPlugin()
