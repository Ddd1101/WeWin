# 手串成品成本模式

本版支持按组成自动核算与独立整件定价，Web 和 Android 均可编辑。

| 行为 | 按组成核算（auto） | 独立定价（manual） |
| --- | --- | --- |
| 采用成本 | 串珠小计 + 配件小计 + 工费 + 弹性成本 | 独立整件成本 |
| 参考测算成本 | 同采用成本 | 组成、工费与弹性成本计算值 |
| 材料成本或组成变化 | 自动更新采用成本 | 仅参考测算成本变化，采用成本保持 |
| 利润展示 | 售价减采用成本 | 售价减独立整件成本 |

独立整件成本已包含整件需要计入的费用，不再自动叠加工费。切换模式或调整独立成本必须填写原因。既有企业负责人/企业管理员及平台管理员拥有编辑权限，企业普通用户仅查看，企业隔离规则沿用原API。

## 查看效果

进入商品管理，选择手串成品并编辑，切换成本模式。独立定价可输入整件成本及原因，组成仍可维护。展开商品可见成本模式、参考测算与采用成本最高/当前/最低；成本历史逐条展示采用金额、参考测算、模式、触发原因、操作人与当时组成。材料涨价导致的参考测算变化也记录，不表示独立采用成本上涨。

Web 和 Android 克价模拟仅测算组成成本与测算利润，不修改采用成本；独立定价时展示提示。Android 商品详情展示模式和参考测算，编辑页支持模式、独立成本及原因；完整历史浏览目前在Web提供。

## API 与迁移

- 创建/更新成品新增 `cost_mode`（auto/manual）、`manual_cost`（非负，两位小数以内）、`cost_note`（400字以内）。进入独立定价必须显式传入manual_cost。成本为0时也有效。
- 未传cost_mode时，更新保留现有模式，创建默认auto。成品cost_price为计算结果，不接受客户端直接覆盖；旧客户端提交cost_price不会覆盖独立成本。
- 成品详情/列表finished对象新增cost_mode、manual_cost、reference_cost、adopted_cost；顶层cost_price为采用成本。
- 历史新增cost_mode、reference_cost、change_type。类型包含legacy、creation、material_change、recalculation、manual_adjustment、mode_switch。模式切换即使金额不变也留记录；名称/图片等无关修改不增加快照。
- `0019_finished_cost_modes` 将已有成品设为auto；旧历史采用金额保持，参考测算仅用旧记录已有分项回填，标记legacy。不得按当前材料价格重建旧金额。
- 当前成本和历史由 `Server/store/views/helpers.py` 的共同计算入口生成；更新在现有product_mutation短事务中完成，失败整体回滚。

## 范围

商品采用成本服务当前报价与利润参考。本版不包含库存批次计价、历史订单成本结转、未来生效协议价、供应商合同管理或审批流。上述业务需独立设计，不能用当前商品成本回算历史订单利润。

## 验证

新增 `store.test_finished_cost_modes` 覆盖自动/独立联动、旧客户端兼容、模式切换、金额与原因校验、组成修改、失败回滚、企业隔离。与 `store.test_deployment` 共22项通过。Web生产构建、Android assembleDebug/lintDebug通过（保留既有依赖等Lint警告）。部署及实际界面验收见 [1.1.0验收记录](finished-cost-validation-2026-11-26.md)。
