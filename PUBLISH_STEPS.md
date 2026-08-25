# Public release steps

## Gate 0 - author metadata finalized

Public author name is fixed as **Ryutaro Yonezu** (given: Ryutaro; family: Yonezu). The final PDF/DOCX have been re-rendered after author insertion.

## 1. GitHub

After the final paper PDF is in `paper/`, run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\PUBLISH_GITHUB_FROM_POWERSHELL.ps1
```

The script uses GitHub CLI authentication, creates a public `joint-portal-dynamics-rna` repository, pushes the finalized public-release package, and creates release `v1.1.0`. It fails closed if the final manuscript files are missing or if any author placeholder remains. It also regenerates `SHA256SUMS.txt` after account-specific metadata is written and verifies every listed hash before any push.

## 2. Zenodo software archive

Connect GitHub to Zenodo, enable the new repository, and archive the `v1.1.0` release. Zenodo will mint a software DOI. Add that DOI to the paper/code metadata in the next paper version.

## 3. Zenodo preprint

Create a new upload as `Publication / Preprint`, upload the finalized PDF, and use `metadata/ZENODO_PREPRINT_METADATA.md`. Add the GitHub URL and software DOI as related identifiers. Publish to mint the preprint DOI.

## 4. arXiv

Submit the finalized PDF to `q-bio.PE`. Use `metadata/ARXIV_METADATA.md`. arXiv accepts PDF submissions when the source is not TeX; first-time/new-category submitters may require endorsement.
