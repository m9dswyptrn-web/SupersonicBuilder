package supersonic
deny[msg] {
  some i
  f := input.changed_files[i]
  endswith(f, ".github/workflows/production.yml")
  not allow_override
  msg := sprintf("Modifying %q requires label security-approve", [f])
}
allow_override {
  some j
  labels := [l.name | l := input.labels[j]]
  labels[_] == "security-approve"
}
