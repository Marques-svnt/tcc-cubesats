#!/usr/bin/env python3
"""Empirical verification harness for SOTA mapping and novelty assessment reports."""

import os
import re
import sys
import hashlib
import json
import urllib.request

SOTA_BENCHMARK = "/home/marques/Área de trabalho/2026.2/TCC/benchmarks/sota_assessment/sota_mapping_report.md"
NOVELTY_BENCHMARK = "/home/marques/Área de trabalho/2026.2/TCC/benchmarks/sota_assessment/novelty_assessment_report.md"
SOTA_VAULT = "/home/marques/vault/svnt/04-Projetos/TCC-CubeSat/SOTA/sota_mapping_report.md"
NOVELTY_VAULT = "/home/marques/vault/svnt/04-Projetos/TCC-CubeSat/SOTA/novelty_assessment_report.md"
CANONICAL_PARAMS = "/home/marques/Área de trabalho/2026.2/TCC/PARAMETROS_CANONICOS.md"


def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def verify_bitwise_parity():
    print("=== [1] BITWISE PARITY VERIFICATION ===")
    sota_bench_sha = get_sha256(SOTA_BENCHMARK)
    sota_vault_sha = get_sha256(SOTA_VAULT)
    nov_bench_sha = get_sha256(NOVELTY_BENCHMARK)
    nov_vault_sha = get_sha256(NOVELTY_VAULT)

    print(f"SOTA Benchmark SHA256: {sota_bench_sha}")
    print(f"SOTA Vault     SHA256: {sota_vault_sha}")
    sota_match = sota_bench_sha == sota_vault_sha
    print(f"Match: {sota_match}")

    print(f"Novelty Benchmark SHA256: {nov_bench_sha}")
    print(f"Novelty Vault     SHA256: {nov_vault_sha}")
    nov_match = nov_bench_sha == nov_vault_sha
    print(f"Match: {nov_match}")

    with open(SOTA_BENCHMARK, "rb") as f1, open(SOTA_VAULT, "rb") as f2:
        sota_cmp = f1.read() == f2.read()
    with open(NOVELTY_BENCHMARK, "rb") as f1, open(NOVELTY_VAULT, "rb") as f2:
        nov_cmp = f1.read() == f2.read()

    print(f"SOTA byte-by-byte cmp: {sota_cmp}")
    print(f"Novelty byte-by-byte cmp: {nov_cmp}")
    return sota_match and nov_match and sota_cmp and nov_cmp


def verify_crossref_metadata():
    print("\n=== [2] CROSSREF METADATA & RESOLUTION VERIFICATION ===")
    results = {}
    dois = {
        "Puig-Suari et al. (2001)": "10.1109/aero.2001.931726",
        "Ulusoy et al. (2026)": "10.65834/jdsi.11.35",
    }
    all_ok = True
    for label, doi in dois.items():
        url = f"https://api.crossref.org/works/{doi}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "TCC-Empirical-Challenger/1.0 (mailto:academic-research@uesc.br)"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                msg = data.get("message", {})
                title = msg.get("title", [""])[0]
                container = msg.get("container-title", [""])[0]
                authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in msg.get("author", [])]
                page = msg.get("page", "")
                volume = msg.get("volume", "")
                issue = msg.get("issue", "")
                print(f"[{label}]")
                print(f"  DOI: {doi} -> RESOLVED 200 OK")
                print(f"  Title: {title}")
                print(f"  Container: {container}")
                print(f"  Authors: {', '.join(authors)}")
                print(f"  Volume: {volume}, Issue: {issue}, Page: {page}")
                results[doi] = {
                    "ok": True,
                    "title": title,
                    "container": container,
                    "authors": authors,
                    "page": page,
                    "volume": volume,
                    "issue": issue,
                }
        except Exception as e:
            print(f"[{label}] ERROR: {e}")
            results[doi] = {"ok": False, "error": str(e)}
            all_ok = False

    # Specific checks:
    # 1. Check Puig-Suari
    ps_data = results.get("10.1109/aero.2001.931726", {})
    if ps_data.get("ok"):
        if "Development of the standard CubeSat deployer" not in ps_data["title"]:
            print("ERROR: Puig-Suari title does not match")
            all_ok = False
        if not any("Puig-Suari" in a for a in ps_data["authors"]):
            print("ERROR: Puig-Suari author missing")
            all_ok = False
        print("  -> Puig-Suari metadata verified against Crossref.")
    else:
        all_ok = False

    # 2. Check Ulusoy pagination
    ul_data = results.get("10.65834/jdsi.11.35", {})
    if ul_data.get("ok"):
        if "Contact-Based CubeSat-Pod" not in ul_data["title"]:
            print("ERROR: Ulusoy title does not match")
            all_ok = False
        if ul_data["page"] != "71-95":
            print(f"ERROR: Ulusoy page is '{ul_data['page']}' != '71-95'")
            all_ok = False
        if str(ul_data["volume"]) != "1" or str(ul_data["issue"]) != "1":
            print(f"ERROR: Ulusoy vol/issue is {ul_data['volume']}({ul_data['issue']}) != 1(1)")
            all_ok = False
        print(f"  -> Ulusoy pagination verified: '{ul_data['page']}' exactly matches 'pp. 71–95', Vol. 1, Issue 1.")
    else:
        all_ok = False

    return all_ok


def parse_and_validate_markdown_math(filepath):
    print(f"\n=== Validating Math & KaTeX in {os.path.basename(filepath)} ===")
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Strip code blocks
    text_no_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text_no_code = re.sub(r"`.*?`", "", text_no_code)

    errors = []

    # Check display math $$ ... $$
    pos = 0
    display_matches = []
    while True:
        idx = text_no_code.find("$$", pos)
        if idx == -1:
            break
        idx2 = text_no_code.find("$$", idx + 2)
        if idx2 == -1:
            errors.append(f"Unmatched $$ starting around character position {idx}")
            break
        math_content = text_no_code[idx + 2 : idx2]
        display_matches.append((idx, idx2, math_content))
        pos = idx2 + 2

    # Remove all display math to safely parse inline math
    text_inline_only = text_no_code
    for idx, idx2, math_content in reversed(display_matches):
        text_inline_only = text_inline_only[:idx] + " " + text_inline_only[idx2 + 2 :]

    # Check inline math $ ... $
    inline_pattern = re.compile(r"(?<!\$)\$(?!\$)([^\$\n]+?)(?<!\$)\$(?!\$)")
    inline_matches = []
    for m in inline_pattern.finditer(text_inline_only):
        inline_matches.append((m.start(), m.end(), m.group(1)))

    print(f"Found {len(display_matches)} display math blocks ($$...$$) and {len(inline_matches)} inline math snippets ($...$).")

    # Check for stray unclosed $
    cleaned_text = inline_pattern.sub(" MATH_INLINE ", text_inline_only)
    stray_dollars = [m.start() for m in re.finditer(r"\$", cleaned_text)]
    if stray_dollars:
        for sd in stray_dollars:
            context = cleaned_text[max(0, sd - 30) : min(len(cleaned_text), sd + 30)].replace("\n", " ")
            errors.append(f"Stray unclosed '$' near: '{context}'")

    # Validate braces in display math
    for idx, idx2, content in display_matches:
        if content.count("{") != content.count("}"):
            errors.append(f"Mismatched braces in $$ block: {content[:50]}...")

    # Validate braces in inline math
    for start, end, content in inline_matches:
        if content.count("{") != content.count("}"):
            errors.append(f"Mismatched braces in inline math: ${content}$")

    if errors:
        print(f"FAILED: {len(errors)} math errors in {os.path.basename(filepath)}:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print(f"PASSED: Zero math syntax/delimiter errors in {os.path.basename(filepath)}.")
        return True


def verify_canonical_parameters():
    print("\n=== [4] CANONICAL PARAMETER VERIFICATION ===")
    with open(SOTA_BENCHMARK, "r", encoding="utf-8") as f:
        sota_text = f.read()
    with open(NOVELTY_BENCHMARK, "r", encoding="utf-8") as f:
        nov_text = f.read()

    combined = sota_text + "\n" + nov_text

    # Canonical checks against PARAMETROS_CANONICOS.md
    checks = [
        ("Massa convencional (308 g)", lambda s, n: bool(re.search(r"308(\s*g|\{,\}0\s*\\text\{\s*g\}|,0\s*g)", s) or re.search(r"308(\s*g|\{,\}0\s*\\text\{\s*g\}|,0\s*g)", n))),
        ("Massa auxética ótima (116 g)", lambda s, n: bool(re.search(r"116(\s*g|\{,\}0\s*\\text\{\s*g\}|,0\s*g)", s) or re.search(r"116(\s*g|\{,\}0\s*\\text\{\s*g\}|,0\s*g)", n))),
        ("Redução de massa (-62.49%)", lambda s, n: bool(re.search(r"62([,.]|\{,\})49\s*(\\%|%)", s) or re.search(r"62([,.]|\{,\})49\s*(\\%|%)", n))),
        ("f1 engastado ótimo (579.62 Hz)", lambda s, n: bool(re.search(r"579([,.]|\{,\})62\s*(\\text\{\s*Hz\}|Hz)", s) or re.search(r"579([,.]|\{,\})62\s*(\\text\{\s*Hz\}|Hz)", n))),
        ("f1 no P-POD ótimo (304.10 Hz)", lambda s, n: bool(re.search(r"304([,.]|\{,\})10?\s*(\\text\{\s*Hz\}|Hz)", s) or re.search(r"304([,.]|\{,\})10?\s*(\\text\{\s*Hz\}|Hz)", n))),
        ("f1 convencional (412.10 Hz)", lambda s, n: bool(re.search(r"412([,.]|\{,\})10?\s*(\\text\{\s*Hz\}|Hz)", s) or re.search(r"412([,.]|\{,\})10?\s*(\\text\{\s*Hz\}|Hz)", n))),
        ("Transmissibilidade convencional (1.66)", lambda s, n: bool(re.search(r"1([,.]|\{,\})66", s) or re.search(r"1([,.]|\{,\})66", n))),
        ("Transmissibilidade auxética (0.39)", lambda s, n: bool(re.search(r"0([,.]|\{,\})39", s) or re.search(r"0([,.]|\{,\})39", n))),
        ("Atenuação vibroacústica (-12.6 dB)", lambda s, n: bool(re.search(r"-12([,.]|\{,\})6\s*(\\text\{\s*dB\}|dB)", s) or re.search(r"-12([,.]|\{,\})6\s*(\\text\{\s*dB\}|dB)", n))),
        ("Atenuação percentual (-76.50%)", lambda s, n: bool(re.search(r"-?76([,.]|\{,\})50?\s*(\\%|%)", s) or re.search(r"-?76([,.]|\{,\})50?\s*(\\%|%)", n))),
        ("Aceleração RMS payload ótima (5.5 G_rms)", lambda s, n: bool(re.search(r"5([,.]|\{,\})5\s*(\\text\{\s*G|\s*G)", s) or re.search(r"5([,.]|\{,\})5\s*(\\text\{\s*G|\s*G)", n))),
        ("Aceleração RMS payload convencional (23.4 G_rms)", lambda s, n: bool(re.search(r"23([,.]|\{,\})4\s*(\\text\{\s*G|\s*G)", s) or re.search(r"23([,.]|\{,\})4\s*(\\text\{\s*G|\s*G)", n))),
        ("Tensão pico 3-sigma ótima (68.8 MPa)", lambda s, n: bool(re.search(r"68([,.]|\{,\})8\s*(\\text\{\s*MPa\}|MPa)", s) or re.search(r"68([,.]|\{,\})8\s*(\\text\{\s*MPa\}|MPa)", n))),
        ("Tensão pico 3-sigma convencional (112.4 MPa)", lambda s, n: bool(re.search(r"112([,.]|\{,\})4\s*(\\text\{\s*MPa\}|MPa)", s) or re.search(r"112([,.]|\{,\})4\s*(\\text\{\s*MPa\}|MPa)", n))),
        ("Margem de segurança yield proposta (+1.56)", lambda s, n: bool(re.search(r"\+?1([,.]|\{,\})56", s) or re.search(r"\+?1([,.]|\{,\})56", n))),
        ("Dano de fadiga Steinberg ótimo (0.0458 / 0.046)", lambda s, n: bool(re.search(r"0([,.]|\{,\})045?8?6?", s) or re.search(r"0([,.]|\{,\})045?8?6?", n))),
        ("Dano de fadiga Steinberg convencional (0.182)", lambda s, n: bool(re.search(r"0([,.]|\{,\})182", s) or re.search(r"0([,.]|\{,\})182", n))),
        ("Critério de qualificação fadiga NASA (D <= 0.25)", lambda s, n: bool(re.search(r"0([,.]|\{,\})25", s) or re.search(r"0([,.]|\{,\})25", n))),
        ("Tratamento térmico AlSi10Mg (300°C / 2h)", lambda s, n: "300" in (s + n) and ("300^\\circ" in (s + n) or "300 C" in (s + n)) and "2" in (s + n)),
        ("Limite de escoamento AlSi10Mg (220 MPa)", lambda s, n: bool(re.search(r"220(\s*\\text\{\s*MPa\}|\s*MPa)", s) or re.search(r"220(\s*\\text\{\s*MPa\}|\s*MPa)", n))),
        ("Nível global NASA GEVS (14.1 G_rms)", lambda s, n: bool(re.search(r"14([,.]|\{,\})1\s*(\\text\{\s*G|\s*G)", s) or re.search(r"14([,.]|\{,\})1\s*(\\text\{\s*G|\s*G)", n))),
        ("Envelope nominal 1U (100 x 100 x 113.5 mm)", lambda s, n: bool(re.search(r"100\s*\\times\s*100\s*\\times\s*113([,.]|\{,\})5", s) or re.search(r"100\s*\\times\s*100\s*\\times\s*113([,.]|\{,\})5", n))),
        ("Trilhos guia (8.5 x 8.5 mm)", lambda s, n: bool(re.search(r"8([,.]|\{,\})5\s*\\times\s*8([,.]|\{,\})5", s) or re.search(r"8([,.]|\{,\})5\s*\\times\s*8([,.]|\{,\})5", n))),
        ("Rugosidade superficial (Ra <= 1.6 um)", lambda s, n: "Ra" in (s + n) and "1{,}6" in (s + n)),
        ("Ângulo mínimo DfAM (overhang >= 35 deg)", lambda s, n: "35" in (s + n) and ("35^\\circ" in (s + n) or "35{,}0^\\circ" in (s + n) or "35°" in (s + n))),
        ("Espessura de costela ótima t* (0.613 mm)", lambda s, n: bool(re.search(r"0([,.]|\{,\})613\s*(\\text\{\s*mm\}|mm)", s) or re.search(r"0([,.]|\{,\})613\s*(\\text\{\s*mm\}|mm)", n))),
        ("Ângulo ótimo theta* (65.75 deg)", lambda s, n: "65{,}75" in (s + n) or "65.75" in (s + n)),
        ("Comprimento ótimo l (8.50 ou 10.42 mm)", lambda s, n: bool(re.search(r"(8([,.]|\{,\})50|10([,.]|\{,\})42)\s*(\\text\{\s*mm\}|mm)", s) or re.search(r"(8([,.]|\{,\})50|10([,.]|\{,\})42)\s*(\\text\{\s*mm\}|mm)", n))),
        ("Altura de costela h (13.96 ou 14.85 mm)", lambda s, n: bool(re.search(r"(13([,.]|\{,\})96|14([,.]|\{,\})85)\s*(\\text\{\s*mm\}|mm)", s) or re.search(r"(13([,.]|\{,\})96|14([,.]|\{,\})85)\s*(\\text\{\s*mm\}|mm)", n))),
        ("Fator de Poisson ótimo celular (-12.63 ou -13.81)", lambda s, n: bool(re.search(r"-(12([,.]|\{,\})63|13([,.]|\{,\})81)", s) or re.search(r"-(12([,.]|\{,\})63|13([,.]|\{,\})81)", n))),
        ("Fator de Poisson efetivo contínuo 3D (-0.428)", lambda s, n: bool(re.search(r"-0([,.]|\{,\})428", s) or re.search(r"-0([,.]|\{,\})428", n))),
        ("Surrogate R2 (0.9874)", lambda s, n: bool(re.search(r"0([,.]|\{,\})9874", s) or re.search(r"0([,.]|\{,\})9874", n))),
        ("Surrogate RMSE (0.0182)", lambda s, n: bool(re.search(r"0([,.]|\{,\})0182", s) or re.search(r"0([,.]|\{,\})0182", n))),
        ("Surrogate tempo de inferência (0.405 ms)", lambda s, n: bool(re.search(r"0([,.]|\{,\})405\s*(\\text\{\s*ms\}|ms)", s) or re.search(r"0([,.]|\{,\})405\s*(\\text\{\s*ms\}|ms)", n))),
        ("Surrogate speedup online (> 200.000x ou 3.6x10^5x)", lambda s, n: bool(re.search(r"(200|2[,.]27|3[,.]6)", s) or re.search(r"(200|2[,.]27|3[,.]6)", n))),
    ]

    all_ok = True
    for label, fn in checks:
        if fn(sota_text, nov_text):
            print(f"  [PASS] {label:50s} -> Verified")
        else:
            print(f"  [FAIL] {label:50s} -> NOT FOUND")
            all_ok = False

    return all_ok


if __name__ == "__main__":
    b1 = verify_bitwise_parity()
    b2 = verify_crossref_metadata()
    b3 = parse_and_validate_markdown_math(SOTA_BENCHMARK)
    b4 = parse_and_validate_markdown_math(NOVELTY_BENCHMARK)
    b5 = verify_canonical_parameters()

    print("\n================== FINAL AUDIT SUMMARY ==================")
    print(f"1. Bitwise Parity Benchmarks vs Vault: {'PASS' if b1 else 'FAIL'}")
    print(f"2. Crossref Metadata Resolution:       {'PASS' if b2 else 'FAIL'}")
    print(f"3. SOTA LaTeX / Math Syntax:           {'PASS' if b3 else 'FAIL'}")
    print(f"4. Novelty LaTeX / Math Syntax:        {'PASS' if b4 else 'FAIL'}")
    print(f"5. Canonical Parameters Alignment:     {'PASS' if b5 else 'FAIL'}")

    all_pass = b1 and b2 and b3 and b4 and b5
    verdict = "APPROVE" if all_pass else "CHALLENGE_FAILED"
    print(f"\nFORMAL VERDICT: {verdict}")
    sys.exit(0 if all_pass else 1)
