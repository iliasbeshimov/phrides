#!/usr/bin/env python3
"""Minimal FastAPI service exposing form submission runner."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from src.automation.forms.form_submitter import ContactPayload, FormSubmissionRunner


class SubmissionRequest(BaseModel):
    dealer: str
    url: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    zip_code: str
    message: str
    headless: Optional[bool] = True


app = FastAPI(title="Auto Form Submission Service", version="0.1.0")
_runner_cache: dict[bool, FormSubmissionRunner] = {}


def get_runner(headless: bool) -> FormSubmissionRunner:
    if headless not in _runner_cache:
        _runner_cache[headless] = FormSubmissionRunner(headless=headless, screenshot_root=Path("artifacts"))
    return _runner_cache[headless]


@app.post("/submit")
async def submit(request: SubmissionRequest):
    runner = get_runner(request.headless)
    payload = ContactPayload(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone=request.phone,
        zip_code=request.zip_code,
        message=request.message,
    )
    try:
        status = await runner.run(request.dealer, request.url, payload)
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {
        "status": status.status,
        "dealer": status.dealer,
        "url": status.url,
        "fields_filled": status.fields_filled,
        "missing_fields": status.missing_fields,
        "dropdown_choices": status.dropdown_choices,
        "checkboxes_checked": status.checkboxes_checked,
        "confirmation_text": status.confirmation_text,
        "artifacts": status.artifacts,
        "errors": status.errors,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("scripts.form_submission.http_service:app", host="0.0.0.0", port=8080, reload=False)
