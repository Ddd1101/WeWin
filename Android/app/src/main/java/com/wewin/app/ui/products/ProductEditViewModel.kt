package com.wewin.app.ui.products

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.wewin.app.data.remote.RetrofitClient
import com.wewin.app.data.remote.dto.AccessoryComponentRequest
import com.wewin.app.data.remote.dto.AccessoryListDto
import com.wewin.app.data.remote.dto.BeadComponentRequest
import com.wewin.app.data.remote.dto.BeadListDto
import com.wewin.app.data.remote.dto.ErrorResponse
import com.wewin.app.data.remote.dto.ProductDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

data class BeadComponent(
    val beadId: Int? = null,
    val skuId: Int? = null,
    val quantity: Int = 1
)

data class AccessoryComponent(
    val accessoryId: Int? = null,
    val skuId: Int? = null,
    val quantity: Int = 1
)

data class ProductEditUiState(
    val isLoading: Boolean = false,
    val isSubmitting: Boolean = false,
    val error: String? = null,
    val submitSuccess: Boolean = false,
    val isEditMode: Boolean = false,
    val initialProduct: ProductDto? = null,
    val beadOptions: List<BeadListDto.BeadListItem> = emptyList(),
    val accessoryOptions: List<AccessoryListDto.AccessoryListItem> = emptyList(),
    // 公共字段
    val code: String = "",
    val name: String = "",
    val productType: String = "bead",
    val purchaseCost: String = "",
    val costPrice: String = "",
    val sellingPrice: String = "",
    val location: String = "",
    val supplier: String = "",
    val isActive: Boolean = true,
    // 串珠特有
    val material: String = "",
    val size: String = "",
    val color: String = "",
    val weight: String = "",
    val qualityLevel: String = "5",
    val remark: String = "",
    // 成品特有
    val laborCost: String = "",
    val elasticCost: String = "",
    // 成品组成
    val beadComponents: List<BeadComponent> = emptyList(),
    val accessoryComponents: List<AccessoryComponent> = emptyList(),
    // 图片
    val imageUri: Uri? = null
)

class ProductEditViewModel(
    private val productId: Int?,
    application: Application
) : AndroidViewModel(application) {

    private val apiService = RetrofitClient.apiService

    private val _uiState = MutableStateFlow(
        ProductEditUiState(isEditMode = productId != null)
    )
    val uiState: StateFlow<ProductEditUiState> = _uiState.asStateFlow()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
        encodeDefaults = true
    }

    init {
        if (productId != null) {
            loadDetail()
        }
    }

    private fun loadDetail() {
        val current = _uiState.value
        if (current.isLoading) return
        _uiState.update { it.copy(isLoading = true, error = null) }
        viewModelScope.launch {
            try {
                val response = apiService.getProductDetail(productId!!)
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body != null) {
                        applyProductToState(body)
                        // 成品需要加载选项
                        if (body.product_type == "finished") {
                            loadFinishedOptions()
                        }
                    } else {
                        _uiState.update {
                            it.copy(isLoading = false, error = "商品详情响应为空")
                        }
                    }
                } else {
                    val errorMsg = parseError(response.code(), response.errorBody()?.string())
                    _uiState.update { it.copy(isLoading = false, error = errorMsg) }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(isLoading = false, error = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        error = "加载失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    private fun applyProductToState(product: ProductDto) {
        var material = ""
        var size = ""
        var color = ""
        var weight = ""
        var qualityLevel = "5"
        var remark = ""
        var laborCost = ""
        var elasticCost = ""
        var beadComponents: List<BeadComponent> = emptyList()
        var accessoryComponents: List<AccessoryComponent> = emptyList()

        product.bead?.let { bead ->
            material = bead.material ?: ""
            size = bead.size?.toString() ?: ""
            color = bead.color ?: ""
            weight = bead.weight.toString()
            qualityLevel = bead.quality_level.toString()
            remark = bead.remark ?: ""
        }
        product.accessory?.let { accessory ->
            material = accessory.material ?: ""
            size = accessory.size?.toString() ?: ""
            color = accessory.color ?: ""
        }
        product.finished?.let { finished ->
            laborCost = finished.labor_cost.toString()
            elasticCost = finished.elastic_cost.toString()
            beadComponents = finished.beads.map { item ->
                BeadComponent(
                    beadId = item.bead_id,
                    skuId = item.sku_id,
                    quantity = item.quantity
                )
            }
            accessoryComponents = finished.accessories.map { item ->
                AccessoryComponent(
                    accessoryId = item.accessory_id,
                    skuId = item.sku_id,
                    quantity = item.quantity
                )
            }
        }

        _uiState.update {
            it.copy(
                isLoading = false,
                initialProduct = product,
                error = null,
                code = product.code,
                name = product.name,
                productType = product.product_type,
                purchaseCost = product.purchase_cost.toString(),
                costPrice = product.cost_price.toString(),
                sellingPrice = product.selling_price.toString(),
                location = product.location ?: "",
                supplier = product.supplier ?: "",
                isActive = product.is_active,
                material = material,
                size = size,
                color = color,
                weight = weight,
                qualityLevel = qualityLevel,
                remark = remark,
                laborCost = laborCost,
                elasticCost = elasticCost,
                beadComponents = beadComponents,
                accessoryComponents = accessoryComponents
            )
        }
    }

    private fun loadFinishedOptions() {
        viewModelScope.launch {
            try {
                val beadsResponse = apiService.getBeads()
                val accessoriesResponse = apiService.getAccessories()
                val beads = if (beadsResponse.isSuccessful) {
                    beadsResponse.body()?.beads ?: emptyList()
                } else emptyList()
                val accessories = if (accessoriesResponse.isSuccessful) {
                    accessoriesResponse.body()?.accessories ?: emptyList()
                } else emptyList()
                _uiState.update {
                    it.copy(beadOptions = beads, accessoryOptions = accessories)
                }
            } catch (e: Exception) {
                // 选项加载失败不阻塞表单填写
            }
        }
    }

    fun setImageUri(uri: Uri?) {
        _uiState.update { it.copy(imageUri = uri) }
    }

    fun submit() {
        val current = _uiState.value
        if (current.isSubmitting) return

        // 校验必填
        if (current.code.isBlank()) {
            _uiState.update { it.copy(error = "请填写货号") }
            return
        }
        if (current.name.isBlank()) {
            _uiState.update { it.copy(error = "请填写商品名称") }
            return
        }
        if (current.productType.isBlank()) {
            _uiState.update { it.copy(error = "请选择商品类型") }
            return
        }

        _uiState.update { it.copy(isSubmitting = true, error = null) }
        viewModelScope.launch {
            try {
                val fields = buildFields(current)
                val imagePart = buildImagePart(current.imageUri)

                val response = if (current.isEditMode) {
                    apiService.updateProductMultipart(productId!!, fields, imagePart)
                } else {
                    apiService.createProductMultipart(fields, imagePart)
                }

                if (response.isSuccessful) {
                    _uiState.update {
                        it.copy(isSubmitting = false, submitSuccess = true, error = null)
                    }
                } else {
                    val errorMsg = parseError(response.code(), response.errorBody()?.string())
                    _uiState.update { it.copy(isSubmitting = false, error = errorMsg) }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(isSubmitting = false, error = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isSubmitting = false,
                        error = "提交失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    private fun buildFields(state: ProductEditUiState): Map<String, RequestBody> {
        val fields = mutableMapOf<String, RequestBody>()
        val textPlain = "text/plain".toMediaTypeOrNull()

        fun put(key: String, value: String) {
            fields[key] = value.toRequestBody(textPlain)
        }

        put("code", state.code)
        put("name", state.name)
        put("product_type", state.productType)
        put("purchase_cost", state.purchaseCost)
        put("cost_price", state.costPrice)
        put("selling_price", state.sellingPrice)
        put("location", state.location)
        put("supplier", state.supplier)
        put("is_active", state.isActive.toString())

        when (state.productType) {
            "bead" -> {
                put("material", state.material)
                put("size", state.size)
                put("color", state.color)
                put("weight", state.weight)
                put("quality_level", state.qualityLevel)
                put("remark", state.remark)
            }
            "accessory" -> {
                put("material", state.material)
                put("size", state.size)
                put("color", state.color)
            }
            "finished" -> {
                put("labor_cost", state.laborCost)
                put("elastic_cost", state.elasticCost)
                val beadRequests = state.beadComponents
                    .filter { it.beadId != null }
                    .map { BeadComponentRequest(it.beadId!!, it.skuId, it.quantity) }
                val accessoryRequests = state.accessoryComponents
                    .filter { it.accessoryId != null }
                    .map { AccessoryComponentRequest(it.accessoryId!!, it.skuId, it.quantity) }
                put(
                    "beads",
                    json.encodeToString(
                        ListSerializer(BeadComponentRequest.serializer()),
                        beadRequests
                    )
                )
                put(
                    "accessories",
                    json.encodeToString(
                        ListSerializer(AccessoryComponentRequest.serializer()),
                        accessoryRequests
                    )
                )
            }
        }

        return fields
    }

    private fun buildImagePart(uri: Uri?): MultipartBody.Part? {
        if (uri == null) return null
        return try {
            val context = getApplication<Application>()
            val inputStream = context.contentResolver.openInputStream(uri) ?: return null
            val bytes = inputStream.use { it.readBytes() }
            val requestBody = bytes.toRequestBody("image/*".toMediaTypeOrNull())
            MultipartBody.Part.createFormData("image", "image.jpg", requestBody)
        } catch (e: Exception) {
            null
        }
    }

    private fun parseError(code: Int, errorBody: String?): String {
        if (errorBody.isNullOrEmpty()) {
            return httpErrorMessage(code)
        }
        return try {
            val errorResponse = json.decodeFromString(
                ErrorResponse.serializer(),
                errorBody
            )
            errorResponse.error ?: errorResponse.message ?: httpErrorMessage(code)
        } catch (e: Exception) {
            httpErrorMessage(code)
        }
    }

    private fun httpErrorMessage(code: Int): String {
        return when (code) {
            401 -> "未授权，请重新登录"
            403 -> "没有访问权限"
            404 -> "商品不存在"
            in 500..599 -> "服务器错误，请稍后重试"
            else -> "请求失败（$code）"
        }
    }
}
