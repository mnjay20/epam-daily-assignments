$docxPath = "c:\Users\dell\Downloads\assignment -1\EPAM_Silicon_Proof_Report.docx"
$pdfPath = "c:\Users\dell\Downloads\assignment -1\EPAM_Silicon_Proof_Report.pdf"

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $doc = $word.Documents.Open($docxPath)
    # 17 is wdExportFormatPDF
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close()
    $word.Quit()
    Write-Output "Successfully converted to PDF via Word COM: $pdfPath"
} catch {
    Write-Output "Word COM Error: $_"
}
