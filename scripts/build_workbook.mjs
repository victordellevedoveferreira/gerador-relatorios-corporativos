import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [processedDirArg, outputPathArg] = process.argv.slice(2);
if (!processedDirArg || !outputPathArg) {
  throw new Error("Uso: node scripts/build_workbook.mjs <data/processed> <saida.xlsx>");
}

const processedDir = path.resolve(processedDirArg);
const outputPath = path.resolve(outputPathArg);
const docsDir = path.resolve(path.dirname(outputPath), "../../docs");

function csvRows(text) {
  const [header, ...rows] = text.trim().replace(/^\uFEFF/, "").split(/\r?\n/);
  const columns = header.split(",");
  return rows.filter(Boolean).map((line) => {
    const values = line.split(",");
    return Object.fromEntries(columns.map((column, index) => [column, values[index] ?? ""]));
  });
}

function money(value) {
  return Number.parseFloat(value);
}

function monthLabel(value) {
  const [year, month] = value.split("-");
  const labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];
  return `${labels[Number(month) - 1]}/${year.slice(2)}`;
}

const [monthlyCsv, areasCsv, transactionsCsv, metricsText] = await Promise.all([
  fs.readFile(path.join(processedDir, "desempenho_mensal.csv"), "utf8"),
  fs.readFile(path.join(processedDir, "desempenho_por_area.csv"), "utf8"),
  fs.readFile(path.join(processedDir, "transacoes_tratadas.csv"), "utf8"),
  fs.readFile(path.join(processedDir, "metricas.json"), "utf8"),
]);
const monthly = csvRows(monthlyCsv);
const areas = csvRows(areasCsv);
const transactions = csvRows(transactionsCsv);
const { metricas, insights } = JSON.parse(metricsText);

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Resumo Executivo");
const performance = workbook.worksheets.add("Desempenho Mensal");
const areaSheet = workbook.worksheets.add("Analise por Area");
const data = workbook.worksheets.add("Dados Tratados");

const navy = "#0B2545";
const blue = "#176B87";
const cyan = "#2CA6A4";
const paleBlue = "#EAF4F8";
const paleGreen = "#E8F5F0";
const orange = "#F4A261";
const gray = "#5E6C84";
const grid = "#D9E2EC";
const white = "#FFFFFF";

for (const sheet of [summary, performance, areaSheet, data]) sheet.showGridLines = false;

summary.mergeCells("A1:P2");
summary.getRange("A1").values = [["RELATÓRIO CORPORATIVO | VISÃO EXECUTIVA"]];
summary.getRange("A1:P2").format = {
  fill: navy,
  font: { bold: true, color: white, size: 18 },
  horizontalAlignment: "left",
  verticalAlignment: "center",
};
summary.mergeCells("A3:P3");
summary.getRange("A3").values = [["Desempenho consolidado • base sintética • período jul/2025 a jun/2026"]];
summary.getRange("A3:P3").format = { font: { color: gray, italic: true, size: 10 }, verticalAlignment: "center" };
summary.getRange("A1:P35").format.rowHeight = 20;
summary.getRange("A:A").format.columnWidth = 21;
summary.getRange("B:B").format.columnWidth = 18;
summary.getRange("C:C").format.columnWidth = 3;
summary.getRange("D:D").format.columnWidth = 21;
summary.getRange("E:E").format.columnWidth = 18;
summary.getRange("F:F").format.columnWidth = 3;
summary.getRange("G:G").format.columnWidth = 21;
summary.getRange("H:H").format.columnWidth = 18;
summary.getRange("I:P").format.columnWidth = 12;

const kpiLabels = [
  ["Receita líquida", "=\"R$ \"&ROUND(SUM('Desempenho Mensal'!B2:B13)/1000000,1)&\" mi\"", paleBlue],
  ["Margem bruta", "=\"R$ \"&ROUND(SUM('Desempenho Mensal'!C2:C13)/1000000,1)&\" mi\"", paleGreen],
  ["Margem consolidada", "=SUM('Desempenho Mensal'!C2:C13)/SUM('Desempenho Mensal'!B2:B13)", "#FFF3E6"],
  ["Ticket médio", "=\"R$ \"&ROUND(SUM('Desempenho Mensal'!B2:B13)/SUM('Desempenho Mensal'!D2:D13),0)", paleBlue],
  ["Transações processadas", "=SUM('Desempenho Mensal'!D2:D13)", paleGreen],
  ["Crescimento último mês", "='Desempenho Mensal'!F13", "#FFF3E6"],
];
const kpiCells = ["A5:B6", "D5:E6", "G5:H6", "A7:B8", "D7:E8", "G7:H8"];
const kpiValueCells = ["A6", "D6", "G6", "A8", "D8", "G8"];
for (let index = 0; index < kpiLabels.length; index += 1) {
  const rangeAddress = kpiCells[index];
  const [label, formula, fill] = kpiLabels[index];
  const [start, end] = rangeAddress.split(":");
  const valueCell = kpiValueCells[index];
  const labelEnd = `${end[0]}${start.slice(1)}`;
  const valueEnd = `${end[0]}${end.slice(1)}`;
  summary.getRange(rangeAddress).format = { fill, borders: { preset: "outside", style: "thin", color: grid } };
  summary.mergeCells(`${start}:${labelEnd}`);
  summary.mergeCells(`${valueCell}:${valueEnd}`);
  summary.getRange(start).values = [[label]];
  summary.getRange(start).format = { font: { bold: true, color: gray, size: 10 } };
  summary.getRange(valueCell).formulas = [[formula]];
  summary.getRange(valueCell).format = { font: { bold: true, color: navy, size: 15 } };
}
summary.getRange("G6").format.numberFormat = "0.0%";
summary.getRange("D8").format.numberFormat = "#,##0";
summary.getRange("G8").format.numberFormat = "0.0%";

summary.mergeCells("A10:H10");
summary.getRange("A10").values = [["INSIGHTS AUTOMÁTICOS"]];
summary.getRange("A10:H10").format = { fill: navy, font: { bold: true, color: white, size: 11 } };
for (let index = 0; index < insights.length; index += 1) {
  const row = index + 11;
  summary.mergeCells(`A${row}:H${row}`);
  summary.getRange(`A${row}`).values = [[`${index + 1}. ${insights[index]}`]];
}
summary.getRange("A11:H15").format = { fill: "#F8FAFC", font: { color: navy, size: 10 }, wrapText: true, verticalAlignment: "center", borders: { preset: "inside", style: "thin", color: grid } };
summary.getRange("A11:H15").format.rowHeight = 28;

const revenueChart = summary.charts.add("line", { chartType: "line", title: "Evolução da receita líquida", hasLegend: false });
const revenueSeries = revenueChart.series.add("Receita líquida");
revenueSeries.categoryFormula = "'Desempenho Mensal'!$A$2:$A$13";
revenueSeries.formula = "'Desempenho Mensal'!$B$2:$B$13";
revenueChart.hasLegend = false;
revenueChart.xAxis = { axisType: "textAxis" };
revenueChart.yAxis = { numberFormatCode: "R$ #,##0" };
revenueChart.setPosition("J5", "P16");
const areaChart = summary.charts.add("bar", { chartType: "bar", title: "Margem bruta por área", hasLegend: false });
const areaSeries = areaChart.series.add("Margem bruta");
areaSeries.categoryFormula = "'Analise por Area'!$A$2:$A$5";
areaSeries.formula = "'Analise por Area'!$C$2:$C$5";
areaChart.hasLegend = false;
areaChart.yAxis = { numberFormatCode: "R$ #,##0" };
areaChart.setPosition("J18", "P32");

const monthlyValues = monthly.map((row) => [
  monthLabel(row.mes), money(row.receita_liquida), money(row.margem_bruta), Number(row.transacoes), Number(row.margem_percentual), Number(row.crescimento_receita),
]);
performance.getRange("A1:F13").values = [["Mês", "Receita líquida", "Margem bruta", "Transações", "Margem %", "Crescimento"], ...monthlyValues];
performance.getRange("A1:F1").format = { fill: navy, font: { bold: true, color: white }, horizontalAlignment: "center" };
performance.getRange("B2:C13").format.numberFormat = "R$ #,##0";
performance.getRange("D2:D13").format.numberFormat = "#,##0";
performance.getRange("E2:F13").format.numberFormat = "0.0%";
performance.getRange("A1:F13").format.borders = { preset: "all", style: "thin", color: grid };
performance.getRange("A1:F13").format.autofitColumns();
performance.getRange("A:A").format.columnWidth = 16;
performance.freezePanes.freezeRows(1);
performance.tables.add("A1:F13", true, "DesempenhoMensal");
performance.getRange("F2:F13").conditionalFormats.add("colorScale", { colors: ["#FADBD8", "#FFFFFF", "#D5F5E3"] });

const areaValues = areas.map((row) => [row.area, money(row.receita_liquida), money(row.margem_bruta), Number(row.margem_percentual)]);
areaSheet.getRange("A1:D5").values = [["Área", "Receita líquida", "Margem bruta", "Margem %"], ...areaValues];
areaSheet.getRange("A1:D1").format = { fill: blue, font: { bold: true, color: white }, horizontalAlignment: "center" };
areaSheet.getRange("B2:C5").format.numberFormat = "R$ #,##0";
areaSheet.getRange("D2:D5").format.numberFormat = "0.0%";
areaSheet.getRange("A1:D5").format.borders = { preset: "all", style: "thin", color: grid };
areaSheet.getRange("A1:D5").format.autofitColumns();
areaSheet.freezePanes.freezeRows(1);
areaSheet.tables.add("A1:D5", true, "AnaliseArea");
areaSheet.getRange("D2:D5").conditionalFormats.add("dataBar", { color: cyan, gradient: true });

const dataHeaders = ["ID", "Data", "Área", "Canal", "Região", "Cliente", "Responsável", "Receita bruta", "Desconto", "Custo", "Receita líquida", "Margem bruta"];
const dataValues = transactions.map((row) => [
  row.id_transacao, row.data, row.area, row.canal, row.regiao, row.cliente, row.responsavel,
  money(row.receita_bruta), money(row.desconto), money(row.custo), money(row.receita_liquida), money(row.margem_bruta),
]);
data.getRangeByIndexes(0, 0, dataValues.length + 1, dataHeaders.length).values = [dataHeaders, ...dataValues];
data.getRange("A1:L1").format = { fill: navy, font: { bold: true, color: white }, horizontalAlignment: "center" };
data.getRange(`H2:L${dataValues.length + 1}`).format.numberFormat = "R$ #,##0.00";
data.getRange(`A1:L${dataValues.length + 1}`).format.borders = { preset: "all", style: "thin", color: grid };
data.getRange("A1:L1").format.autofitColumns();
data.getRange("F:F").format.columnWidth = 18;
data.getRange("G:G").format.columnWidth = 16;
data.freezePanes.freezeRows(1);
data.tables.add(`A1:L${dataValues.length + 1}`, true, "DadosTratados");

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.mkdir(docsDir, { recursive: true });
const preview = await workbook.render({ sheetName: "Resumo Executivo", autoCrop: "all", scale: 1, format: "png" });
const previewBytes = new Uint8Array(await preview.arrayBuffer());
await fs.writeFile(path.join(docsDir, "planilha-preview.png"), previewBytes);
await fs.writeFile(path.join(docsDir, "preview.png"), previewBytes);
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);

const check = await workbook.inspect({ kind: "table,formula,drawing", sheetId: "Resumo Executivo", range: "A1:P32", maxChars: 3000 });
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" });
console.log(check.ndjson ?? check);
console.log(errors.ndjson ?? errors);
console.log(`Planilha criada: ${outputPath}`);
