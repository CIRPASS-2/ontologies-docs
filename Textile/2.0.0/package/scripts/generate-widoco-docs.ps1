param([string[]]$OnlyModules = @())
$ErrorActionPreference = "Stop"
$GenerationWorkspace = (Get-Location).Path
$InitialWidocoTemps = @(Get-ChildItem -Directory -Filter "tmp*" | Select-Object -ExpandProperty FullName)

$Widoco        = "tools\widoco-1.4.25_JDK-17.jar"
$Jaxb          = "tools\jaxb-api-2.3.1.jar"
$OutputRoot    = "docs\widoco"
$EditorialRoot = "widoco\sections"
$LandingGenerator = "scripts\generate-widoco-index.py"

$modules = @(
    "assessment",
    "associated-materials",
    "connector",
    "context",
    "core",
    "durability",
    "indicator",
    "process",
    "recyclability",
    "repairability",
    "soc",
    "structure"
)
if ($OnlyModules.Count -gt 0) {
    foreach ($selectedModule in $OnlyModules) {
        if ($selectedModule -notin $modules) { throw "Unknown module: $selectedModule" }
    }
    $modules = @($modules | Where-Object { $_ -in $OnlyModules })
}

if (-not (Test-Path $Widoco)) {
    throw "WIDOCO JAR not found: $Widoco"
}

if (-not (Test-Path $Jaxb)) {
    throw "JAXB API JAR not found: $Jaxb"
}

if (-not (Test-Path $LandingGenerator)) {
    throw "Landing-page generator not found: $LandingGenerator"
}

New-Item -ItemType Directory -Force $OutputRoot | Out-Null


# ------------------------------------------------------------
# Encoding helpers
# ------------------------------------------------------------

$Utf8Strict = New-Object System.Text.UTF8Encoding(
    $false,
    $true
)

$Utf8NoBom = New-Object System.Text.UTF8Encoding(
    $false
)

$Windows1252 = [System.Text.Encoding]::GetEncoding(1252)

$TextExtensions = @(
    ".ttl",
    ".nt",
    ".rdf",
    ".owl",
    ".jsonld",
    ".html",
    ".htm",
    ".css",
    ".js",
    ".mjs",
    ".json",
    ".md",
    ".txt",
    ".csv",
    ".xml",
    ".svg",
    ".yml",
    ".yaml"
)


function Remove-WidocoResidualTempFolders {

    Get-ChildItem `
        -Directory `
        -Filter "tmp*" `
        -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -match '^tmp\d+$' -and $_.FullName -notin $InitialWidocoTemps -and $_.Parent.FullName -eq $GenerationWorkspace
    } |
    Remove-Item `
        -Recurse `
        -Force `
        -ErrorAction SilentlyContinue
}


function Normalize-WidocoGeneratedTextEncoding {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $files = Get-ChildItem `
        $Root `
        -Recurse `
        -File

    foreach ($file in $files) {

        $extension = $file.Extension.ToLowerInvariant()

        if ($TextExtensions -notcontains $extension) {
            continue
        }

        $path = $file.FullName
        $bytes = [System.IO.File]::ReadAllBytes($path)

        $encodingChanged = $false

        try {
            $text = $Utf8Strict.GetString($bytes)
        }
        catch [System.Text.DecoderFallbackException] {

            $text = $Windows1252.GetString($bytes)
            $encodingChanged = $true
        }

        # Normalise all generated textual artifacts to LF.
        $normalised = $text.Replace(
            "`r`n",
            "`n"
        ).Replace(
            "`r",
            "`n"
        )

        if ($encodingChanged -or $normalised -ne $text) {

            [System.IO.File]::WriteAllText(
                $path,
                $normalised,
                $Utf8NoBom
            )

            Write-Host `
                "Normalised generated text to UTF-8/LF: $path"
        }
    }
}

function Remove-WidocoTrailingWhitespace {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $files = Get-ChildItem `
        $Root `
        -Recurse `
        -File

    foreach ($file in $files) {

        $extension = $file.Extension.ToLowerInvariant()

        if ($TextExtensions -notcontains $extension) {
            continue
        }

        $path = $file.FullName
        $bytes = [System.IO.File]::ReadAllBytes($path)

        try {
            $text = $Utf8Strict.GetString($bytes)
        }
        catch [System.Text.DecoderFallbackException] {
            continue
        }

        $cleaned = [System.Text.RegularExpressions.Regex]::Replace(
            $text,
            '[ \t]+(?=\r?$)',
            '',
            [System.Text.RegularExpressions.RegexOptions]::Multiline
        )

        if ($cleaned -ne $text) {

            [System.IO.File]::WriteAllText(
                $path,
                $cleaned,
                $Utf8NoBom
            )

            Write-Host "Removed trailing whitespace: $path"
        }
    }
}

function Repair-WidocoRelativeLinks {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Root
    )

    $files = Get-ChildItem `
        $Root `
        -Recurse `
        -File |
    Where-Object {
        $_.Name -eq "provenance-en.ttl" -or
        $_.Name -eq "provenance-en.html"
    }

    foreach ($file in $files) {

        $text = [System.IO.File]::ReadAllText(
            $file.FullName,
            $Utf8Strict
        )

        $corrected = $text.Replace(
            '..\index-en.html',
            '../index-en.html'
        )

        if ($corrected -ne $text) {

            [System.IO.File]::WriteAllText(
                $file.FullName,
                $corrected,
                $Utf8NoBom
            )

            Write-Host `
                "Repaired portable provenance link: $($file.FullName)"
        }
    }
}


# ------------------------------------------------------------
# Module generation
# ------------------------------------------------------------

foreach ($module in $modules) {

    $ontology = "ontology\textile-$module.ttl"
    $output   = Join-Path $OutputRoot $module
    $sections = Join-Path $EditorialRoot $module

    if (-not (Test-Path $ontology)) {
        throw "Ontology not found: $ontology"
    }

    Write-Host ""
    Write-Host "========================================"
    Write-Host "Generating documentation: $module"
    Write-Host "========================================"

    try {

        if (Test-Path $output) {
            $resolvedOutput = (Resolve-Path -LiteralPath $output).Path
            $expectedOutputRoot = [System.IO.Path]::GetFullPath((Join-Path $GenerationWorkspace $OutputRoot))
            if ([System.IO.Path]::GetDirectoryName($resolvedOutput) -ne $expectedOutputRoot) {
                throw "Unexpected WIDOCO output directory: $resolvedOutput"
            }
            Remove-Item -LiteralPath $resolvedOutput -Recurse -Force
        }

        java -cp "$Widoco;$Jaxb" `
            widoco.gui.GuiController `
            -ontFile $ontology `
            -outFolder $output `
            -getOntologyMetadata `
            -rewriteAll `
            -webVowl `
            -lang en

        if ($LASTEXITCODE -ne 0) {
            throw "WIDOCO failed for $module"
        }


        # ----------------------------------------------------
        # Inject human-authored editorial sections
        # ----------------------------------------------------

        if (Test-Path $sections) {

            $editorialFiles = @(
                "abstract-en.html",
                "introduction-en.html",
                "description-en.html",
                "references-en.html"
            )

            foreach ($file in $editorialFiles) {

                $source = Join-Path $sections $file
                $target = Join-Path "$output\sections" $file

                if (Test-Path $source) {

                    Copy-Item `
                        $source `
                        $target `
                        -Force

                    Write-Host `
                        "Injected editorial section: $module/$file"
                }
            }
        }


        # ----------------------------------------------------
        # Normalise WIDOCO-generated publication artifacts
        # ----------------------------------------------------

        Normalize-WidocoGeneratedTextEncoding `
            -Root $output

        Repair-WidocoRelativeLinks `
            -Root $output

        Remove-WidocoTrailingWhitespace `
            -Root $output


        # ----------------------------------------------------
        # Restore the exact canonical ontology serialization
        # This must be the final operation on ontology.ttl.
        # ----------------------------------------------------

        Copy-Item `
            $ontology `
            (Join-Path $output "ontology.ttl") `
            -Force

        python scripts/sync-widoco-rdf.py $module
        if ($LASTEXITCODE -ne 0) { throw "Canonical RDF synchronisation failed for $module" }

        python scripts/widoco_annotations.py $module
        if ($LASTEXITCODE -ne 0) { throw "Annotation-property documentation failed for $module" }

        Write-Host "Canonical TTL restored: $module"

        Write-Host "Completed: $module"
    }
    finally {

        Remove-WidocoResidualTempFolders
    }
}


# ------------------------------------------------------------
# Generate ontology-network landing page
# ------------------------------------------------------------

Write-Host ""
Write-Host "========================================"
Write-Host "Generating ontology-network landing page"
Write-Host "========================================"

python $LandingGenerator

if ($LASTEXITCODE -ne 0) {
    throw "Landing-page generation failed."
}

$LandingTarget = Join-Path $OutputRoot "index.html"

if (-not (Test-Path $LandingTarget)) {
    throw "Generated landing page not found: $LandingTarget"
}

Write-Host "Landing page generated: $LandingTarget"

# ------------------------------------------------------------
# Placeholder verification
# ------------------------------------------------------------

Write-Host ""
Write-Host "========================================"
Write-Host "Checking generated documentation"
Write-Host "========================================"

$placeholderResults = @()

foreach ($module in $modules) {

    $sectionFolder = Join-Path `
        "$OutputRoot\$module" `
        "sections"

    if (-not (Test-Path $sectionFolder)) {
        continue
    }

    foreach ($file in @(
        "abstract-en.html",
        "introduction-en.html",
        "description-en.html",
        "references-en.html"
    )) {

        $path = Join-Path $sectionFolder $file

        if (Test-Path $path) {

            $hits = Select-String `
                -Path $path `
                -Pattern @(
                    "placeholder text",
                    "place holder text",
                    "Add your references here"
                ) `
                -SimpleMatch

            if ($hits) {
                $placeholderResults += $hits
            }
        }
    }
}

if ($placeholderResults.Count -gt 0) {

    Write-Warning `
        "WIDOCO placeholder content remains:"

    $placeholderResults |
        Select-Object Path, LineNumber, Line |
        Format-Table -AutoSize
}
else {

    Write-Host `
        "No WIDOCO placeholders detected."
}


Write-Host ""
Write-Host "Documentation generation completed."
