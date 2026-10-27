$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$diagramModels = @(
    @{ Name='textile-soc'; Title='Textile SoC - October 2026 CORE / 2.0.0 candidate'; Rows=@(
        @('TextileChemicalSubstance','subClassOf','CORE Substance'),
        @('Textile positive presence','subClassOf','CORE SubstancePresence'),
        @('CORE SubstancePresence','concernsSubstance','CORE SubstanceOfConcern'),
        @('Presence-specific qualification','hasSoCCriterion','Criterion A / B / C / D'),
        @('TextileTypeDQualification','explicit scope','Owning product; no propagation'),
        @('TextileConcentrationInformation','direct CORE carriers','Scalar OR range endpoints + unit'),
        @('MaximumConcentration','uses numericalValue','Never maximumNumericalValue'),
        @('Textile threshold purpose','subClassOf','CORE ThresholdOfSubstanceOfConcern'),
        @('Exact / maximum / range value roles','subClassOf','Shared Textile QuantitativeValue'),
        @('Structured location / denominator','membership','Forward / inverse / non-textile part'),
        @('ThresholdEvaluation','ownership','Concentration of its owning presence'),
        @('Textile handling information','subClassOf','CORE SubstanceManagementInstruction')
    )},
    @{ Name='textile-associated-materials'; Title='Associated Materials - retained structural distinctions'; Rows=@(
        @('TextileChemicalSubstance','subClassOf','CORE Substance'),
        @('NonTextileComponent','subClassOf','TextileProductPart'),
        @('TextileMaterialGroup','subClassOf','TextileProductPart'),
        @('NonTextileComponentMaterialGroup','distinct from','The component itself'),
        @('TextileFibreCompositionMaterialGroup','subClassOf','FibreCompositionComponent AND group'),
        @('NonTextileComponent','hasComponentMaterial','CORE MaterialOfComposition'),
        @('Structural part / material group','no universal typing','Product OR MaterialOfComposition')
    )},
    @{ Name='textile-recyclability'; Title='Recyclability - retained Textile model and migrated SoC boundary'; Rows=@(
        @('RecyclabilityBarrier','refersToSubstancePresence','Existing Textile presence IRI'),
        @('Textile substance presence','subClassOf','CORE SubstancePresence'),
        @('RecycledContentDeclaration','Textile-owned','Separate from recyclability'),
        @('Actual textile recycling event','event alignment','CORE ProductEvent'),
        @('Textile process execution','independent type','No ProductEvent inference'),
        @('Below / above / equal threshold','comparison outcome','No compliance or exemption inference')
    )},
    @{ Name='textile-ontology-network-overview'; Title='Textile 2.0.0 candidate - 20-graph offline runtime closure'; Rows=@(
        @('Network entry point 2.0.0','closure includes','13 Textile graphs: entry + 12 modules'),
        @('Textile SOC / Associated Materials','updated 2.0.0','Retained Textile sector semantics'),
        @('Recyclability / network entry','updated 2.0.0','Other module bytes remain 1.1.2'),
        @('SOC / CON MIREOT 2.0.0','bounded sources','SOC 2.2.0 / CON 2.4.0'),
        @('P_DPP / EVENT MIREOT 2.0.0','bounded sources','P_DPP 2.2.0 / EVENT 1.0.0'),
        @('ACTOR / MAT MIREOT 2.0.0','compatible reuse','ACTOR 2.2.0 / MAT 1.1.0'),
        @('SI MIREOT 1.1.2','unchanged','Approved measurement-unit support'),
        @('Historical 1.1.2 / SoC 1.1.3','separate catalogue','Exact preserved bytes; outside runtime'),
        @('IDENT / COMP / LCA','not integrated','No full CORE import')
    )}
)
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
foreach ($model in $diagramModels) {
    $canvasWidth = 1600
    $canvasHeight = 100 + 130 * $model.Rows.Count
    $bitmap = New-Object System.Drawing.Bitmap($canvasWidth, $canvasHeight)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.Clear([System.Drawing.Color]::White)
    $font = New-Object System.Drawing.Font('Arial', 15)
    $smallFont = New-Object System.Drawing.Font('Arial', 12)
    $titleFont = New-Object System.Drawing.Font('Arial', 20, [System.Drawing.FontStyle]::Bold)
    $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(65,90,120),2)
    $leftBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(235,245,255))
    $rightBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(238,248,237))
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $graphics.DrawString($model.Title,$titleFont,[System.Drawing.Brushes]::Black,20,15)
    $svg = New-Object System.Text.StringBuilder
    [void]$svg.AppendLine("<svg xmlns=`"http://www.w3.org/2000/svg`" width=`"$canvasWidth`" height=`"$canvasHeight`" viewBox=`"0 0 $canvasWidth $canvasHeight`">")
    [void]$svg.AppendLine('<rect width="100%" height="100%" fill="white"/><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#415a78"/></marker></defs>')
    $title = [System.Security.SecurityElement]::Escape($model.Title)
    [void]$svg.AppendLine("<text x=`"20`" y=`"40`" font-family=`"Arial`" font-size=`"26`" font-weight=`"bold`">$title</text>")
    $rowIndex = 0
    foreach ($row in $model.Rows) {
        $y = 75 + 130*$rowIndex
        $middle = $y+40
        foreach ($side in 0,1) {
            $x = if ($side -eq 0) { 20 } else { 1040 }
            $brush = if ($side -eq 0) { $leftBrush } else { $rightBrush }
            $color = if ($side -eq 0) { '#ebf5ff' } else { '#eef8ed' }
            $label = $row[$side*2]
            $rect = New-Object System.Drawing.RectangleF($x,$y,540,80)
            $graphics.FillRectangle($brush,$rect)
            $graphics.DrawRectangle($pen,$x,$y,540,80)
            $graphics.DrawString($label,$font,[System.Drawing.Brushes]::Black,$rect,$format)
            $escaped = [System.Security.SecurityElement]::Escape($label)
            [void]$svg.AppendLine("<rect x=`"$x`" y=`"$y`" width=`"540`" height=`"80`" fill=`"$color`" stroke=`"#415a78`"/><text x=`"$($x+270)`" y=`"$($middle+7)`" text-anchor=`"middle`" font-family=`"Arial`" font-size=`"20`">$escaped</text>")
        }
        $graphics.DrawLine($pen,570,$middle,1020,$middle)
        $graphics.DrawLine($pen,1020,$middle,1008,($middle-6))
        $graphics.DrawLine($pen,1020,$middle,1008,($middle+6))
        $labelRect = New-Object System.Drawing.RectangleF(570,($y-5),450,35)
        $graphics.DrawString($row[1],$smallFont,[System.Drawing.Brushes]::Black,$labelRect,$format)
        $edge = [System.Security.SecurityElement]::Escape($row[1])
        [void]$svg.AppendLine("<path d=`"M570,$middle L1020,$middle`" stroke=`"#415a78`" stroke-width=`"2`" marker-end=`"url(#arrow)`"/><text x=`"795`" y=`"$($y+17)`" text-anchor=`"middle`" font-family=`"Arial`" font-size=`"16`">$edge</text>")
        $rowIndex++
    }
    [void]$svg.AppendLine('</svg>')
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) "diagrams/$($model.Name).svg"),$svg.ToString().Replace("`r`n","`n"),$utf8NoBom)
    $bitmap.Save((Join-Path (Get-Location) "diagrams/$($model.Name).png"),[System.Drawing.Imaging.ImageFormat]::Png)
    $format.Dispose();$pen.Dispose();$leftBrush.Dispose();$rightBrush.Dispose();$font.Dispose();$smallFont.Dispose();$titleFont.Dispose();$graphics.Dispose();$bitmap.Dispose()
    Write-Output "Generated SVG/PNG: $($model.Name)"
}
