package com.wewin.app.data.remote.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
enum class PurchaseListStatus(val value: String, val display: String) {
    @SerialName("pending") PENDING("pending", "待采购"),
    @SerialName("in_progress") IN_PROGRESS("in_progress", "进行中"),
    @SerialName("completed") COMPLETED("completed", "已完成");
}

@Serializable
enum class PurchaseItemStatus(val value: String, val display: String) {
    @SerialName("pending") PENDING("pending", "待采购"),
    @SerialName("partially_purchased") PARTIALLY_PURCHASED("partially_purchased", "已购买部分"),
    @SerialName("purchased") PURCHASED("purchased", "已购买");
}

@Serializable
data class PurchaseItemDto(
    val id: Int,
    @SerialName("purchase_list_id") val purchaseListId: Int,
    @SerialName("product_id") val productId: Int? = null,
    @SerialName("sku_id") val skuId: Int? = null,
    @SerialName("product_type") val productType: String = "",
    @SerialName("product_name") val productName: String = "",
    @SerialName("sku_code") val skuCode: String = "",
    val quantity: Double = 0.0,
    val unit: String = "克",
    @SerialName("unit_price") val unitPrice: Double = 0.0,
    val supplier: String = "",
    val location: String = "",
    @SerialName("quality_level") val qualityLevel: Int? = null,
    val material: String = "",
    val size: Int? = null,
    val color: String = "",
    val remark: String = "",
    val status: String = "pending",
    @SerialName("status_display") val statusDisplay: String = "",
    @SerialName("purchased_quantity") val purchasedQuantity: Double = 0.0,
    @SerialName("created_at") val createdAt: String = "",
    @SerialName("updated_at") val updatedAt: String = ""
)

@Serializable
data class PurchaseListDto(
    val id: Int,
    val title: String = "",
    val status: String = "pending",
    @SerialName("status_display") val statusDisplay: String = "",
    @SerialName("planned_date") val plannedDate: String = "",
    val notes: String = "",
    @SerialName("assignee_id") val assigneeId: Int? = null,
    @SerialName("assignee_name") val assigneeName: String = "",
    @SerialName("created_by_id") val createdById: Int? = null,
    @SerialName("created_by_name") val createdByName: String = "",
    @SerialName("company_id") val companyId: Int? = null,
    @SerialName("created_at") val createdAt: String = "",
    @SerialName("updated_at") val updatedAt: String = "",
    val items: List<PurchaseItemDto> = emptyList(),
    @SerialName("total_count") val totalCount: Int = 0,
    @SerialName("purchased_count") val purchasedCount: Int = 0
)

@Serializable
data class PurchaseListSummaryDto(
    val id: Int,
    val title: String = "",
    val status: String = "pending",
    @SerialName("status_display") val statusDisplay: String = "",
    @SerialName("planned_date") val plannedDate: String = "",
    @SerialName("assignee_name") val assigneeName: String = ""
)

@Serializable
data class PurchaseListResponse(
    val lists: List<PurchaseListDto> = emptyList(),
    @SerialName("total_count") val totalCount: Int = 0,
    val page: Int = 1,
    @SerialName("page_size") val pageSize: Int = 50
)

@Serializable
data class UncompletedListsResponse(
    val lists: List<PurchaseListSummaryDto> = emptyList()
)

@Serializable
data class PurchaseItemResponse(
    val item: PurchaseItemDto,
    @SerialName("list_status") val listStatus: String = ""
)

@Serializable
data class CarryOverResponse(
    val list: PurchaseListDto,
    val item: PurchaseItemDto
)
