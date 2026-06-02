/**
 * AINews arrival trigger — runs in Google Apps Script (script.google.com).
 *
 * Why this exists: GitHub Actions cron is best-effort and on this repo lags
 * 3–6 hours behind schedule, so ainews-watch.yml cannot poll punctually on its
 * own.  This script runs on a reliable Apps Script time-driven trigger (every
 * 10 min), checks Gmail natively, and the moment an unforwarded AINews issue
 * exists it dispatches the workflow through the GitHub API —
 * `workflow_dispatch` runs start within seconds, with none of the
 * schedule-queue delay.
 *
 * Dedup stays where it already lives: the workflow labels the mail
 * (radar-forwarded) only after a successful send, and this script's query
 * excludes that label.  Re-dispatching while a run is still in flight is
 * harmless — the workflow's concurrency group queues the run and its light
 * check exits early once the label lands.
 *
 * One-time setup (~5 min):
 *   1. Create a fine-grained GitHub PAT at
 *      https://github.com/settings/personal-access-tokens/new
 *        - Repository access: Only select repositories → this repo
 *        - Permissions: Actions → Read and write
 *   2. Go to https://script.google.com logged in as the Gmail account that
 *      RECEIVES the AINews newsletter → New project → paste this file.
 *   3. Project Settings (gear icon) → Script Properties → add:
 *        GITHUB_TOKEN = <the PAT from step 1>
 *        GITHUB_REPO  = <owner/repo, e.g. waynehacking8/content-radar>
 *   4. In the editor, run checkAINews() once to grant Gmail + network
 *      permissions.
 *   5. Triggers (clock icon) → Add Trigger → checkAINews → Time-driven →
 *      Minutes timer → Every 10 minutes.  Set "notify me immediately" on
 *      failure so a broken PAT surfaces in your inbox.
 */

// Defaults — override any of these via a Script Property of the same name.
var DEFAULTS = {
  WORKFLOW_FILE: 'ainews-watch.yml',
  WORKFLOW_REF: 'main',
  // 2d window (not 1d): if this trigger breaks for a day (expired PAT, outage),
  // the next working check still catches yesterday's issue. The radar-forwarded
  // label — not this window — is what prevents duplicate sends.
  // Keep in sync with AINEWS_FRESH_WINDOW in content_radar/config.py.
  GMAIL_QUERY: 'subject:AINews newer_than:2d -label:radar-forwarded',
};

function checkAINews() {
  var props = PropertiesService.getScriptProperties();
  var prop = function (key) {
    return (props.getProperty(key) || DEFAULTS[key] || '').trim();
  };

  var threads = GmailApp.search(prop('GMAIL_QUERY'), 0, 1);
  if (threads.length === 0) {
    return; // nothing new — the common case; stay silent
  }

  var repo = prop('GITHUB_REPO');
  var token = prop('GITHUB_TOKEN');
  if (!repo || !token) {
    throw new Error('Missing Script Properties: set GITHUB_REPO and GITHUB_TOKEN');
  }

  var url =
    'https://api.github.com/repos/' +
    repo +
    '/actions/workflows/' +
    prop('WORKFLOW_FILE') +
    '/dispatches';
  var response = UrlFetchApp.fetch(url, {
    method: 'post',
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    contentType: 'application/json',
    payload: JSON.stringify({ ref: prop('WORKFLOW_REF') }),
    muteHttpExceptions: true,
  });

  var code = response.getResponseCode();
  if (code !== 204) {
    // Throw so the trigger's failure notification emails you. Truncate the
    // body — GitHub error payloads can be long and this lands in the exec log.
    throw new Error(
      'workflow_dispatch failed: HTTP ' + code + ' — ' +
        response.getContentText().substring(0, 300)
    );
  }
  Logger.log(
    'AINews found ("%s") → dispatched %s',
    threads[0].getFirstMessageSubject(),
    prop('WORKFLOW_FILE')
  );
}
