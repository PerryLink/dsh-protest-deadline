import { describeTablePlugin } from './table-plugin-suite.ts'
import { Config } from '../src/config.ts'
import { parseMaterial, runCheck, SPEC } from '../src/model.ts'
import { buildView } from '../src/view.ts'
import { inject, name, resolvePackageFile, TOOL_NAME } from '../src/index.ts'

describeTablePlugin({
  name,
  inject,
  TOOL_NAME,
  resolvePackageFile,
  Config,
  rulesFile: 'rules/protest-deadline.yaml',
  parseMaterial,
  runCheck,
  buildView,
  columnNames: SPEC.columns,
  samples: {
    good: {
      project: '某某设备采购项目',
      projectNo: 'ZC-2026-018',
      rows: [
        {
          序号: 'ZY-2026-001',
          质疑人: '某某科技有限公司',
          质疑提出日期: '2026-03-02',
          答复期限: '2026-03-09',
          实际答复日期: '2026-03-06',
          投诉日期: '2026-03-12',
          处理状态: '已答复',
        },
      ],
    },
    unknownColumn: { rows: [{ 备注: '甲' }] },
  },
})
