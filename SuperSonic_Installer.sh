#!/usr/bin/env bash
set -e
echo "SonicBuilder Supersonic 4-Pack Installer"
echo "This will copy pack docs into ./docs/<pack> and keep them modular."
for z in SonicBuilder_*_v1.zip; do
  name="${z%.zip}"
  mkdir -p "install/$name"
  unzip -o "$z" -d "install/$name" >/dev/null
  if [ -d "install/$name/docs" ]; then
    mkdir -p "docs/$name"
    cp -R "install/$name/docs/"* "docs/$name/"
  fi
done
echo "Done. Next: unzip pipeline/SonicBuilder_DocsPipeline_Integrated.zip at repo root and run make build-docs."
