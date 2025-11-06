"""Webhook endpoint to sync tasks from Notion into the WhatsApp bot database."""
from fastapi import APIRouter, Request, Header, HTTPException
from notion_client import Client
from notion_client.errors import APIResponseError
from typing import Dict, Any, List, Optional

from src.config.settings import settings
from src.utils.logger import logger


router = APIRouter(prefix="/notion", tags=["notion"])


def _ensure_configuration():
    if not settings.NOTION_API_KEY:
        logger.error("NOTION_API_KEY is not configured")
        raise HTTPException(status_code=500, detail="Notion integration not configured")

    target_db = settings.NOTION_GROQ_TASKS_DB_ID or settings.NOTION_DATABASE_ID
    if not target_db:
        logger.error("No target Notion database configured")
        raise HTTPException(status_code=500, detail="Target Notion database not configured")

    return Client(auth=settings.NOTION_API_KEY), target_db


def _extract_title(props: Dict[str, Any]) -> str:
    title_prop = props.get("Task") or props.get("Name") or props.get("Título") or {}
    parts = title_prop.get("title", [])
    if not parts:
        return ""
    return "".join(part.get("plain_text") or "" for part in parts)


def _extract_rich_text(props: Dict[str, Any], key: str) -> Optional[str]:
    prop = props.get(key, {})
    parts = prop.get("rich_text", [])
    if not parts:
        return None
    return "".join(part.get("plain_text") or "" for part in parts)


def _extract_select(props: Dict[str, Any], key: str) -> Optional[str]:
    select = props.get(key, {}).get("select")
    if not select:
        return None
    return select.get("name")


def _extract_people(props: Dict[str, Any], keys: List[str]) -> List[Dict[str, str]]:
    for key in keys:
        people_prop = props.get(key)
        if not people_prop:
            continue

        people = people_prop.get("people")
        if isinstance(people, list) and people:
            return [{"id": person.get("id")} for person in people if person.get("id")]

        # Sometimes assignees are stored as rich text
        if people_prop.get("type") in {"rich_text", "title"}:
            entries = people_prop.get(people_prop["type"], [])
            assignees = []
            for entry in entries:
                text = entry.get("plain_text") or entry.get("text", {}).get("content")
                if text:
                    assignees.append({"name": text})
            if assignees:
                return assignees

    return []


def _map_status(status_name: Optional[str]) -> Optional[str]:
    # Placeholder for future mapping logic if needed.
    return status_name


@router.post("/webhook")
async def handle_notion_webhook(request: Request, authorization: str = Header(None)):
    """Receive Notion automation webhook and mirror the page into the bot's Notion database."""
    token = settings.NOTION_WEBHOOK_TOKEN
    if token and authorization != f"Bearer {token}":
        logger.warning("Unauthorized Notion webhook attempt")
        raise HTTPException(status_code=401, detail="Unauthorized")

    payload = await request.json()
    page_id = (
        payload.get("page_id")
        or payload.get("trigger", {}).get("page", {}).get("id")
        or payload.get("data", {}).get("id")
    )

    if not page_id:
        logger.warning("Notion webhook received without page_id")
        return {"ok": True, "skipped": "missing_page_id"}

    notion, target_db = _ensure_configuration()

    try:
        page = notion.pages.retrieve(page_id=page_id)
    except APIResponseError as exc:
        logger.error(f"Failed to retrieve Notion page {page_id}: {exc}")
        raise HTTPException(status_code=400, detail=f"Failed to retrieve Notion page: {exc}") from exc

    props = page.get("properties", {})

    title = _extract_title(props) or "Untitled"
    notes = (
        _extract_rich_text(props, "Notes")
        or _extract_rich_text(props, "Descrição")
        or _extract_rich_text(props, "Description")
    )
    status_name = (
        _extract_select(props, "Status")
        or _extract_select(props, "Status 1")
        or _extract_select(props, "Workflow")
    )
    assignees = _extract_people(props, ["Assignees", "Responsável", "Responsaveis", "Owner", "Assigned"])
    project = _extract_select(props, "Project") or _extract_select(props, "Projeto")
    page_url = page.get("url")

    # Look for existing mirror page using origin_page_id rich text field
    try:
        existing = notion.databases.query(
            database_id=target_db,
            filter={"property": "origin_page_id", "rich_text": {"equals": page_id}}
        )
    except APIResponseError as exc:
        logger.error(f"Failed to query target Notion database: {exc}")
        raise HTTPException(status_code=400, detail=f"Failed to query target database: {exc}") from exc

    def build_properties() -> Dict[str, Any]:
        properties: Dict[str, Any] = {
            "Task": {"title": [{"type": "text", "text": {"content": title}}]},
        }

        mapped_status = _map_status(status_name)
        if mapped_status:
            properties["Status"] = {"select": {"name": mapped_status}}

        if notes:
            properties["Notes"] = {
                "rich_text": [{"type": "text", "text": {"content": notes}}]
            }

        if assignees:
            # If assignees are plain text fallback, keep as rich_text
            if assignees and "id" not in assignees[0]:
                properties["Assignees"] = {
                    "rich_text": [
                        {"type": "text", "text": {"content": ", ".join(a.get("name") for a in assignees if a.get("name"))}}
                    ]
                }
            else:
                properties["Assignees"] = {"people": assignees}

        if project:
            properties["Project"] = {"select": {"name": project}}

        if page_url:
            properties["Source"] = {"url": page_url}

        return properties

    properties = build_properties()

    if existing.get("results"):
        target_page_id = existing["results"][0]["id"]
        logger.info(f"Updating mirrored Notion task {target_page_id} from source {page_id}")
        try:
            notion.pages.update(page_id=target_page_id, properties=properties)
        except APIResponseError as exc:
            logger.error(f"Failed to update mirrored Notion page {target_page_id}: {exc}")
            raise HTTPException(status_code=400, detail=f"Failed to update mirrored page: {exc}") from exc
        return {"ok": True, "updated": target_page_id}

    logger.info(f"Creating mirrored Notion task for source {page_id}")
    properties["origin_page_id"] = {
        "rich_text": [{"type": "text", "text": {"content": page_id}}]
    }

    try:
        notion.pages.create(parent={"database_id": target_db}, properties=properties)
    except APIResponseError as exc:
        logger.error(f"Failed to create mirrored Notion page from {page_id}: {exc}")
        raise HTTPException(status_code=400, detail=f"Failed to create mirrored page: {exc}") from exc

    return {"ok": True, "created": True}
