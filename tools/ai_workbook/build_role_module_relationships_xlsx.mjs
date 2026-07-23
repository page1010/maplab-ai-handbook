#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [csvPath, xlsxPath, previewPath] = process.argv.slice(2);
if (!csvPath || !xlsxPath) {
  throw new Error(
    "Usage: build_role_module_relationships_xlsx.mjs <input.csv> <output.xlsx> [preview.png]",
  );
}

const nodeModulesRoot = process.env.CODEX_NODE_MODULES;
const artifactToolUrl = nodeModulesRoot
  ? pathToFileURL(
      path.join(
        nodeModulesRoot,
        "@oai",
        "artifact-tool",
        "dist",
        "artifact_tool.mjs",
      ),
    ).href
  : "@oai/artifact-tool";
const { SpreadsheetFile, Workbook } = await import(artifactToolUrl);

const csvText = await fs.readFile(csvPath, "utf8");
const workbook = await Workbook.fromCSV(csvText, {
  sheetName: "Relationships",
});
const relationships = workbook.worksheets.getItem("Relationships");
const usedRange = relationships.getUsedRange();
const rowCount = usedRange.rowCount;
const lastRow = rowCount;

relationships.showGridLines = false;
relationships.freezePanes.freezeRows(1);
relationships.freezePanes.freezeColumns(3);

const header = relationships.getRange("A1:M1");
header.format = {
  fill: "#17324D",
  font: { bold: true, color: "#FFFFFF", size: 11 },
  verticalAlignment: "center",
  wrapText: true,
  borders: {
    bottom: { style: "medium", color: "#0B1F33" },
  },
};
header.format.rowHeight = 34;

const dataRange = relationships.getRange(`A2:M${lastRow}`);
dataRange.format = {
  font: { color: "#243447", size: 10 },
  verticalAlignment: "top",
  wrapText: true,
  borders: {
    insideHorizontal: { style: "thin", color: "#E4EAF0" },
  },
};
dataRange.format.rowHeight = 30;

const widths = {
  A: 12,
  B: 44,
  C: 44,
  D: 20,
  E: 23,
  F: 22,
  G: 10,
  H: 20,
  I: 13,
  J: 30,
  K: 48,
  L: 12,
  M: 52,
};
for (const [column, width] of Object.entries(widths)) {
  relationships.getRange(`${column}1:${column}${lastRow}`).format.columnWidth =
    width;
}
relationships.getRange(`I2:I${lastRow}`).format.numberFormat = "#,##0";
relationships.getRange(`A2:A${lastRow}`).format.horizontalAlignment = "center";
relationships.getRange(`G2:G${lastRow}`).format.horizontalAlignment = "center";
relationships.getRange(`I2:I${lastRow}`).format.horizontalAlignment = "right";
relationships.getRange(`L2:L${lastRow}`).format.horizontalAlignment = "center";

relationships
  .getRange(`G2:G${lastRow}`)
  .conditionalFormats.add("containsText", {
    text: "false",
    format: {
      fill: "#FDE7E7",
      font: { color: "#A61B1B", bold: true },
    },
  });
relationships
  .getRange(`E2:E${lastRow}`)
  .conditionalFormats.add("containsText", {
    text: "restricted_reference",
    format: {
      fill: "#FFF3CD",
      font: { color: "#7A5300", bold: true },
    },
  });
relationships
  .getRange(`L2:L${lastRow}`)
  .conditionalFormats.add("containsText", {
    text: "high",
    format: {
      fill: "#FFE2CC",
      font: { color: "#9C3D10", bold: true },
    },
  });

const relationshipTable = relationships.tables.add(
  `A1:M${lastRow}`,
  true,
  "RoleModuleRelationships",
);
relationshipTable.style = "TableStyleMedium2";
relationshipTable.showBandedRows = true;
relationshipTable.showFilterButton = true;

const summary = workbook.worksheets.add("Summary");
summary.showGridLines = false;
summary.getRange("A1:F2").merge();
summary.getRange("A1").values = [["MAPLAB Dynamic Role Relationships"]];
summary.getRange("A1:F2").format = {
  fill: "#17324D",
  font: { bold: true, color: "#FFFFFF", size: 20 },
  verticalAlignment: "center",
};
summary.getRange("A3:F3").merge();
summary.getRange("A3").values = [
  [
    "Generated from the canonical role-module CSV. Edit the CSV/generator, then rebuild this workbook.",
  ],
];
summary.getRange("A3:F3").format = {
  fill: "#E9F2F8",
  font: { italic: true, color: "#35566F", size: 10 },
  verticalAlignment: "center",
};
summary.getRange("A5:B9").values = [
  ["Metric", "Value"],
  ["Relationship rows", null],
  ["Missing source rows", null],
  ["High-risk rows", null],
  ["Restricted references", null],
];
summary.getRange("B6").formulas = [[`=COUNTA(Relationships!A2:A${lastRow})`]];
summary.getRange("B7").formulas = [
  [`=COUNTIF(Relationships!G2:G${lastRow},"false")`],
];
summary.getRange("B8").formulas = [
  [`=COUNTIF(Relationships!L2:L${lastRow},"high")`],
];
summary.getRange("B9").formulas = [
  [`=COUNTIF(Relationships!E2:E${lastRow},"restricted_reference")`],
];
summary.getRange("A5:B5").format = {
  fill: "#2C6E8F",
  font: { bold: true, color: "#FFFFFF" },
  borders: {
    bottom: { style: "medium", color: "#17324D" },
  },
};
summary.getRange("A6:A9").format = {
  fill: "#F3F7FA",
  font: { bold: true, color: "#243447" },
  borders: {
    insideHorizontal: { style: "thin", color: "#D6E0E8" },
  },
};
summary.getRange("B6:B9").format = {
  font: { bold: true, color: "#17324D", size: 14 },
  horizontalAlignment: "right",
  numberFormat: "#,##0",
  borders: {
    insideHorizontal: { style: "thin", color: "#D6E0E8" },
  },
};
summary.getRange("D5:F5").merge();
summary.getRange("D5").values = [["Reading guide"]];
summary.getRange("D5:F5").format = {
  fill: "#2C6E8F",
  font: { bold: true, color: "#FFFFFF" },
};
summary.getRange("D6:F9").merge();
summary.getRange("D6").values = [
  [
    "Use Relationships filters to trace each role to its required files, runtime targets, affected systems, and risk. Red marks missing sources, amber marks restricted references, and orange marks high-risk rows.",
  ],
];
summary.getRange("D6:F9").format = {
  fill: "#F7FAFC",
  font: { color: "#35566F", size: 11 },
  verticalAlignment: "top",
  wrapText: true,
  borders: {
    preset: "outside",
    style: "thin",
    color: "#D6E0E8",
  },
};
summary.getRange("A11:F11").merge();
summary.getRange("A11").values = [["Workbook contract"]];
summary.getRange("A11:F11").format = {
  fill: "#DDEBF3",
  font: { bold: true, color: "#17324D" },
};
summary.getRange("A12:F14").merge();
summary.getRange("A12").values = [
  [
    "The Relationships sheet is the complete Excel-readable mapping. It is generated from role_module_relationships.csv by tools/ai_workbook/build_role_module_relationships_xlsx.mjs. Do not hand-edit generated rows.",
  ],
];
summary.getRange("A12:F14").format = {
  fill: "#FFFFFF",
  font: { color: "#35566F", size: 11 },
  verticalAlignment: "top",
  wrapText: true,
  borders: {
    preset: "outside",
    style: "thin",
    color: "#D6E0E8",
  },
};
summary.getRange("A1:F14").format.rowHeight = 24;
summary.getRange("A1:F2").format.rowHeight = 34;
summary.getRange("A3:F3").format.rowHeight = 28;
summary.getRange("A5:B9").format.rowHeight = 26;
summary.getRange("D6:F9").format.rowHeight = 28;
summary.getRange("A12:F14").format.rowHeight = 28;
summary.getRange("A1:A14").format.columnWidth = 28;
summary.getRange("B1:B14").format.columnWidth = 16;
summary.getRange("C1:C14").format.columnWidth = 3;
summary.getRange("D1:F14").format.columnWidth = 22;
summary.freezePanes.freezeRows(3);

const inspect = await workbook.inspect({
  kind: "sheet,table,formula",
  maxChars: 5000,
  tableMaxRows: 6,
  tableMaxCols: 13,
  tableMaxCellChars: 80,
});
console.log(inspect.ndjson);

await fs.mkdir(path.dirname(xlsxPath), { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(xlsxPath);

if (previewPath) {
  await fs.mkdir(path.dirname(previewPath), { recursive: true });
  const preview = await workbook.render({
    sheetName: "Summary",
    autoCrop: "all",
    scale: 1.5,
    format: "png",
  });
  await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));
}
