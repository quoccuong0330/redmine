from datetime import date, datetime
from html import escape


# Colour tokens (inline-safe for email clients)
CLR = {
    'header_bg': '#2c3e50',
    'green':     '#2f9e44',
    'green_bg':  '#d3f9d8',
    'red':       '#e03131',
    'red_bg':    '#ffe3e3',
    'blue':      '#1971c2',
    'blue_bg':   '#dbe4ff',
    'muted':     '#868e96',
    'border':    '#e9ecef',
    'bg_light':  '#f8f9fa',
}

CARD_STYLE = (
    'border:1px solid #e9ecef;border-radius:6px;padding:12px 14px;'
    'margin-bottom:8px;display:flex;align-items:flex-start;gap:12px;'
    'font-family:Arial,sans-serif;'
)


def _tag(text: str, color: str, bg: str) -> str:
    style = (
        f'display:inline-block;padding:2px 8px;border-radius:4px;'
        f'font-size:11px;font-weight:600;background:{bg};color:{color};'
    )
    return f'<span style="{style}">{escape(text)}</span>'


def _section_title(icon: str, label: str) -> str:
    style = (
        'font-size:11px;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.8px;color:#868e96;margin:0 0 12px;'
        'font-family:Arial,sans-serif;'
    )
    return f'<p style="{style}">{icon} {label}</p>'


def _empty_state(msg: str) -> str:
    style = (
        'text-align:center;padding:20px;color:#adb5bd;font-size:13px;'
        'border:1px dashed #dee2e6;border-radius:6px;'
        'font-family:Arial,sans-serif;'
    )
    return f'<div style="{style}">{msg}</div>'


def _render_time_entries(entries: list, redmine_url: str) -> str:
    if not entries:
        return _empty_state('No time logged today yet')
    rows = []
    for e in entries:
        hours_str = f"{e['hours']:.1f}h"
        issue_link = (
            f'<a href="{redmine_url}/issues/{e["issue_id"]}" '
            f'style="color:#1a1a1a;text-decoration:none;" target="_blank">'
            f'#{e["issue_id"]} — {escape(e["issue_title"])}</a>'
            if e.get('issue_id') else escape(e['issue_title'])
        )
        rows.append(f'''
        <div style="{CARD_STYLE}">
          <div style="font-size:16px;flex-shrink:0">✅</div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:14px;font-weight:500;margin:0 0 4px;">{issue_link}</div>
            <div style="font-size:12px;color:#868e96;">
              {escape(e["project"])} &nbsp;&middot;&nbsp;
              {_tag(e["activity"], CLR["green"], CLR["green_bg"])}
            </div>
          </div>
          <div style="background:#f8f9fa;border:1px solid #dee2e6;border-radius:20px;
                      padding:3px 10px;font-size:12px;font-weight:600;
                      color:#495057;flex-shrink:0;">{hours_str}</div>
        </div>''')
    return ''.join(rows)


def _render_issues(issues: list, tag_label: str, tag_color: str, tag_bg: str,
                   icon: str, empty_msg: str) -> str:
    if not issues:
        return _empty_state(empty_msg)
    rows = []
    for i in issues:
        rows.append(f'''
        <div style="{CARD_STYLE}">
          <div style="font-size:16px;flex-shrink:0">{icon}</div>
          <div style="flex:1;min-width:0;">
            <div style="font-size:14px;font-weight:500;margin:0 0 4px;">
              <a href="{i["url"]}" style="color:#1a1a1a;text-decoration:none;" target="_blank">
                #{i["id"]} — {escape(i["subject"])}
              </a>
            </div>
            <div style="font-size:12px;color:#868e96;">
              {escape(i["project"])} &nbsp;&middot;&nbsp;
              {_tag(tag_label, tag_color, tag_bg)}
            </div>
          </div>
        </div>''')
    return ''.join(rows)


def render_digest_email(
    time_entries: list,
    due_today: list,
    due_tomorrow: list,
    redmine_url: str,
) -> str:
    today = date.today()
    day_name = today.strftime('%A')
    date_str = today.strftime('%d %B %Y')

    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:20px;background:#f0f2f5;font-family:Arial,sans-serif;">
<div style="max-width:640px;margin:0 auto;background:#fff;border-radius:8px;
            overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.1);">

  <!-- Header -->
  <div style="background:{CLR["header_bg"]};padding:28px 32px 24px;color:#fff;">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
      <h1 style="margin:0;font-size:20px;font-weight:700;">📋 Daily Work Digest</h1>
      <span style="background:rgba(255,255,255,.15);border-radius:20px;padding:4px 12px;
                   font-size:12px;font-weight:600;">{day_name}</span>
    </div>
    <div style="font-size:13px;opacity:.65;">{date_str} &middot; Generated at 17:00</div>
  </div>

  <!-- Stats bar -->
  <div style="display:flex;background:#f8f9fa;border-bottom:1px solid #e9ecef;">
    <div style="flex:1;padding:16px 20px;text-align:center;border-right:1px solid #e9ecef;">
      <div style="font-size:22px;font-weight:700;color:{CLR["green"]};line-height:1;margin-bottom:4px;">
        {len(time_entries)}</div>
      <div style="font-size:11px;color:{CLR["muted"]};text-transform:uppercase;letter-spacing:.5px;">
        Logged today</div>
    </div>
    <div style="flex:1;padding:16px 20px;text-align:center;border-right:1px solid #e9ecef;">
      <div style="font-size:22px;font-weight:700;color:{CLR["red"]};line-height:1;margin-bottom:4px;">
        {len(due_today)}</div>
      <div style="font-size:11px;color:{CLR["muted"]};text-transform:uppercase;letter-spacing:.5px;">
        Open today</div>
    </div>
    <div style="flex:1;padding:16px 20px;text-align:center;">
      <div style="font-size:22px;font-weight:700;color:{CLR["blue"]};line-height:1;margin-bottom:4px;">
        {len(due_tomorrow)}</div>
      <div style="font-size:11px;color:{CLR["muted"]};text-transform:uppercase;letter-spacing:.5px;">
        Due tomorrow</div>
    </div>
  </div>

  <!-- Section 1: Worked today -->
  <div style="padding:24px 32px 0;">
    {_section_title("✅", "Worked on today")}
    {_render_time_entries(time_entries, redmine_url)}
  </div>

  <hr style="border:none;border-top:1px solid #e9ecef;margin:24px 32px 0;"/>

  <!-- Section 2: Due today, still open -->
  <div style="padding:24px 32px 0;">
    {_section_title("❌", "Due today — still open")}
    {_render_issues(due_today, "Due today", CLR["red"], CLR["red_bg"],
                    "⚠️", "All clear — nothing overdue today 🎉")}
  </div>

  <hr style="border:none;border-top:1px solid #e9ecef;margin:24px 32px 0;"/>

  <!-- Section 3: Due tomorrow -->
  <div style="padding:24px 32px 24px;">
    {_section_title("📅", "Due tomorrow")}
    {_render_issues(due_tomorrow, "Due tomorrow", CLR["blue"], CLR["blue_bg"],
                    "🔵", "Nothing due tomorrow")}
  </div>

  <!-- Footer -->
  <div style="padding:16px 32px 20px;background:#f8f9fa;border-top:1px solid #e9ecef;
              display:flex;justify-content:space-between;align-items:center;">
    <div style="font-size:12px;color:#adb5bd;">
      Redmine Digest &middot; <a href="{redmine_url}" style="color:#adb5bd;">{redmine_url}</a>
    </div>
    <div style="font-size:11px;color:#ced4da;">⚠️ Log time before 17:00 for accurate report</div>
  </div>

</div>
</body>
</html>'''


def render_brief_email(time_entries: list, redmine_url: str) -> str:
    now = datetime.now()
    total_hours = sum(e.get('hours', 0) for e in time_entries)
    time_str = now.strftime('%H:%M')
    date_str = now.strftime('%a %d %b %Y')

    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:20px;background:#f0f2f5;font-family:Arial,sans-serif;">
<div style="max-width:640px;margin:0 auto;background:#fff;border-radius:8px;
            overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.1);">

  <!-- Header -->
  <div style="background:{CLR["header_bg"]};padding:20px 32px;color:#fff;
              display:flex;align-items:center;justify-content:space-between;">
    <div>
      <div style="font-size:16px;font-weight:700;margin-bottom:2px;">⏱ Progress Update</div>
      <div style="font-size:12px;opacity:.65;">{date_str}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:28px;font-weight:700;line-height:1;color:{CLR["green"]};">{total_hours:.1f}h</div>
      <div style="font-size:11px;opacity:.65;margin-top:2px;">logged as of {time_str}</div>
    </div>
  </div>

  <!-- Time entries -->
  <div style="padding:20px 32px;">
    {_render_time_entries(time_entries, redmine_url)}
  </div>

</div>
</body>
</html>'''
