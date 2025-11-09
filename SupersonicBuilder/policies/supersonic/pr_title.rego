package supersonic
deny[msg] {
  not valid_title
  msg := sprintf("PR title must start with feat|fix|chore|docs|ci|build|refactor|test|perf: got %q", [input.title])
}
valid_title { startswith(lower(input.title), "feat:") }
else { startswith(lower(input.title), "fix:") }
else { startswith(lower(input.title), "chore:") }
else { startswith(lower(input.title), "docs:") }
else { startswith(lower(input.title), "ci:") }
else { startswith(lower(input.title), "build:") }
else { startswith(lower(input.title), "refactor:") }
else { startswith(lower(input.title), "test:") }
else { startswith(lower(input.title), "perf:") }
