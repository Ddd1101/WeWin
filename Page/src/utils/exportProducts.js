import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

export function exportFinishedProducts(products) {
  const wb = XLSX.utils.book_new()

  // 单 Sheet：展开式明细，每个成品一行汇总，紧跟其串珠和配件行
  const rows = []
  products.forEach(p => {
    // 成品行
    rows.push({
      '类型': '成品',
      '成品货号': p.code,
      '成品名称': p.name,
      '货号': '',
      'SKU名称': '',
      '数量': '',
      '克价(元/克)': '',
      '单价': '',
      '小计': '',
      '规格(mm)': '',
      '品级': '',
      '成本价格': p.cost_price,
      '售卖价格': p.selling_price,
      '利润率(%)': p.selling_price > 0 ? ((p.selling_price - p.cost_price) / p.selling_price * 100).toFixed(2) : '0',
      '工费': p.finished?.labor_cost ?? 0,
      '弹性成本': p.finished?.elastic_cost ?? 0,
      '库位': p.location || '',
      '供应商': p.supplier || '',
      '状态': p.is_active ? '启用' : '禁用'
    })
    // 串珠行
    ;(p.finished?.beads || []).forEach(b => {
      rows.push({
        '类型': '串珠',
        '成品货号': p.code,
        '成品名称': p.name,
        '货号': b.bead_code || '',
        'SKU名称': b.sku?.name || b.sku?.sku_name || b.bead_name,
        '数量': b.quantity,
        '克价(元/克)': b.bead_purchase_cost ?? '',
        '单价': b.bead_cost_price,
        '小计': (b.bead_cost_price * b.quantity).toFixed(2),
        '规格(mm)': b.bead_size || '',
        '品级': b.bead_quality_level || '',
        '成本价格': '',
        '售卖价格': '',
        '利润率(%)': '',
        '工费': '',
        '弹性成本': '',
        '库位': '',
        '供应商': '',
        '状态': ''
      })
    })
    // 配件行
    ;(p.finished?.accessories || []).forEach(a => {
      rows.push({
        '类型': '配件',
        '成品货号': p.code,
        '成品名称': p.name,
        '货号': a.accessory_code || '',
        'SKU名称': a.sku?.name || a.sku?.sku_name || a.accessory_name,
        '数量': a.quantity,
        '克价(元/克)': '',
        '单价': a.accessory_cost_price,
        '小计': (a.accessory_cost_price * a.quantity).toFixed(2),
        '规格(mm)': '',
        '品级': '',
        '成本价格': '',
        '售卖价格': '',
        '利润率(%)': '',
        '工费': '',
        '弹性成本': '',
        '库位': '',
        '供应商': '',
        '状态': ''
      })
    })
  })

  const ws = XLSX.utils.json_to_sheet(rows)
  XLSX.utils.book_append_sheet(wb, ws, '商品明细')

  // 生成并下载
  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([wbout], { type: 'application/octet-stream' })
  const timestamp = new Date().toISOString().slice(0, 10)
  saveAs(blob, `手串成品明细_${timestamp}.xlsx`)
}
