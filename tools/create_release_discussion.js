/**
 * Node script for actions/github-script step.
 * Creates (or updates) a Discussion for a given tag using CHANGELOG + summary.
 * Inputs via env:
 *   GITHUB_REPOSITORY, GITHUB_TOKEN, RELEASE_TAG
 * Reads files:
 *   CHANGELOG.md (top is used) and optional RELEASE_SUMMARY.md
 */
module.exports = async ({github, core, context}) => {
  const {owner, repo} = context.repo;
  const tag = process.env.RELEASE_TAG;
  const fs = require('fs');

  // Read body from CHANGELOG head + optional summary
  let body = "";
  try { body = fs.readFileSync("CHANGELOG.md", "utf8"); } catch {}
  let summary = "";
  try { summary = fs.readFileSync("RELEASE_SUMMARY.md", "utf8"); } catch {}
  const title = `Release ${tag}`;

  // Pick a category: prefer "Announcements", else the first available
  const { data: cats } = await github.rest.discussions.listCategories({ owner, repo });
  let cat = cats.find(c => c.name.toLowerCase() === "announcements") || cats[0];
  if (!cat) {
    core.info("Discussions not enabled or no categories; skipping.");
    return;
  }

  const full = (summary ? (summary + "\n\n---\n") : "") + body;

  // Try to find an existing discussion with the same title
  // (There is no direct search API; this keeps it simple: create a new one.)
  const disc = await github.rest.discussions.create({
    owner, repo,
    title,
    body: full.slice(0, 65500),
    category_id: cat.id
  });

  core.info(`Discussion created: ${disc.data.html_url}`);
};
