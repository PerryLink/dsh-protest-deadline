/**
 * dsh-protest-deadline — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'protest_deadline'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  seq: ['序号', '编号', '质疑函编号', 'seq'],
  protestant: ['质疑人', '异议人', '供应商名称', 'protestant'],
  target: ['被质疑人', '被异议人', '采购人', '采购代理机构', 'target'],
  raisedAt: ['质疑提出日期', '提出日期', '异议提出日期', 'raisedAt'],
  receivedAt: ['答复收到日期', '收到答复日期', '答复日期', 'receivedAt'],
  replyDueAt: ['答复期限', '法定答复期限', '应答复日期', 'replyDueAt'],
  replyAt: ['实际答复日期', '答复时间', 'replyAt'],
  complaintAt: ['投诉日期', '提起投诉日期', 'complaintAt'],
  complaintDueAt: ['投诉期限', '投诉截止日期', 'complaintDueAt'],
  status: ['处理状态', '状态', 'status'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'records', '异议'],
  columns: COLUMNS,
  header: {
  project: ['project', '项目名称', '采购项目名称'],
  projectNo: ['projectNo', '项目编号', '采购编号'],
  agency: ['agency', '采购代理机构', '代理机构'],
  purchaser: ['purchaser', '采购人'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '质疑提出日期',
  'raisedAt',
  '质疑函编号',
  'seq',
  '投诉日期',
  'complaintAt',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
