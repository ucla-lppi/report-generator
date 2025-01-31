import aspose.words as aw

# Load the PDF
doc = aw.Document("templates/cwfs2025_0128_5-1.pdf")

# Perform find and replace
doc.range.replace("{{NAME}}", "John Doe", aw.replacing.FindReplaceOptions(aw.replacing.FindReplaceDirection.FORWARD))

# Save the modified document
doc.save("output.pdf")