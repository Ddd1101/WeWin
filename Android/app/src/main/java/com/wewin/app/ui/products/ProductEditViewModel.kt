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
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.CancellationException
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.io.File
import java.util.concurrent.atomic.AtomicReference
import okhttp3.RequestBody.Companion.asRequestBody
import com.wewin.app.data.remote.dto.SkuDto

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

data class ClothingSkuInput(val size: String = "", val cost: String = "", val price: String = "")

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
    val costMode: String = "auto",
    val manualCost: String = "",
    val costNote: String = "",
    val laborCost: String = "",
    val elasticCost: String = "",
    // 成品组成
    val beadComponents: List<BeadComponent> = emptyList(),
    val accessoryComponents: List<AccessoryComponent> = emptyList(),
    // 图片
    val imageUri: Uri? = null,
    val removeImage: Boolean = false,
    val fabric: String = "",
    val clothingSize: String = "",
    val season: String = "",
    val gender: String = "",
    val ageRange: String = "",
    val clothingSkus: List<ClothingSkuInput> = emptyList()
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
                costMode = product.finished?.cost_mode ?: "auto",
                manualCost = product.finished?.manual_cost?.toString() ?: "",
                costNote = "",
                sellingPrice = product.selling_price.toString(),
                location = product.location ?: "",
                supplier = product.supplier ?: "",
                isActive = product.is_active,
                material = material,
                size = size,
                color = product.children_clothing?.color ?: color,
                weight = weight,
                qualityLevel = qualityLevel,
                remark = remark,
                laborCost = laborCost,
                elasticCost = elasticCost,
                beadComponents = beadComponents,
                accessoryComponents = accessoryComponents,
                fabric = product.children_clothing?.fabric.orEmpty(),
                clothingSize = product.children_clothing?.size.orEmpty(),
                season = product.children_clothing?.season.orEmpty(),
                gender = product.children_clothing?.gender.orEmpty(),
                ageRange = product.children_clothing?.age_range.orEmpty(),
                clothingSkus = if (product.product_type == "children_clothing") product.skus.map {
                    ClothingSkuInput(it.size?.toString() ?: it.name.orEmpty(), it.cost_price.toString(), it.selling_price.toString())
                } else emptyList()
            )
        }
    }

    fun loadFinishedOptions() {
        viewModelScope.launch {
            try {
                val beadsResponse = apiService.getBeads()
                val accessoriesResponse = apiService.getAccessories()
                if (!beadsResponse.isSuccessful || !accessoriesResponse.isSuccessful) {
                    val failed = if (!beadsResponse.isSuccessful) beadsResponse else accessoriesResponse
                    _uiState.update { it.copy(error = parseError(failed.code(), failed.errorBody()?.string())) }
                    return@launch
                }
                val beads = if (beadsResponse.isSuccessful) {
                    beadsResponse.body()?.beads ?: emptyList()
                } else emptyList()
                val accessories = if (accessoriesResponse.isSuccessful) {
                    accessoriesResponse.body()?.accessories ?: emptyList()
                } else emptyList()
                _uiState.update {
                    it.copy(beadOptions = beads, accessoryOptions = accessories)
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                _uiState.update { it.copy(error = "材料选项加载失败，请刷新材料") }
            }
        }
    }

    fun updateForm(change: (ProductEditUiState) -> ProductEditUiState) {
        if (_uiState.value.isSubmitting) return
        val oldType = _uiState.value.productType
        _uiState.update { change(it).copy(error = null) }
        if (oldType != "finished" && _uiState.value.productType == "finished") loadFinishedOptions()
    }

    fun removeImage() {
        _uiState.update { it.copy(imageUri = null, removeImage = true, error = null) }
    }

    fun setImageUri(uri: Uri?) {
        _uiState.update { it.copy(imageUri = uri, removeImage = false, error = null) }
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

        val numericValues = listOf(current.purchaseCost, current.costPrice, current.sellingPrice, current.weight, current.laborCost, current.elasticCost, current.manualCost)
        if (numericValues.any { it.isNotBlank() && (it.toBigDecimalOrNull()?.signum() ?: -1) < 0 }) {
            _uiState.update { it.copy(error = "成本、售价和重量必须是非负数字") }; return
        }
        if (current.productType == "finished") {
            val prior = current.initialProduct?.finished
            val switched = prior != null && prior.cost_mode != current.costMode
            val manualChanged = current.costMode == "manual" && (prior == null || current.manualCost.toBigDecimalOrNull()?.compareTo(prior.manual_cost.toBigDecimal()) != 0)
            if (current.costMode == "manual" && current.manualCost.toBigDecimalOrNull() == null) {
                _uiState.update { it.copy(error = "请填写独立整件成本") }; return
            }
            if ((switched || manualChanged) && current.costNote.isBlank()) {
                _uiState.update { it.copy(error = "调整独立成本或切换模式，请填写原因") }; return
            }
        }
        if (current.productType == "bead" && current.qualityLevel.toIntOrNull() !in 1..10) {
            _uiState.update { it.copy(error = "品质等级须为1至10") }; return
        }
        if (current.productType in listOf("bead", "accessory") && current.size.isNotBlank() && current.size.toIntOrNull() == null) {
            _uiState.update { it.copy(error = "规格须为整数") }; return
        }
        if ((current.beadComponents.any { it.beadId == null || it.quantity <= 0 } || current.accessoryComponents.any { it.accessoryId == null || it.quantity <= 0 }) && current.productType == "finished") {
            _uiState.update { it.copy(error = "请选择组成材料，并填写正整数数量") }; return
        }
        if (current.productType == "children_clothing") {
            val sizes = current.clothingSkus.map { it.size.trim().uppercase() }
            if (sizes.isEmpty() || sizes.any { it.isBlank() } || sizes.distinct().size != sizes.size) {
                _uiState.update { it.copy(error = "请填写至少一个不重复的尺码") }; return
            }
            if (current.clothingSkus.any { it.cost.toBigDecimalOrNull()?.signum()?.let { sign -> sign < 0 } != false || (it.price.isNotBlank() && (it.price.toBigDecimalOrNull()?.signum() ?: -1) < 0) }) {
                _uiState.update { it.copy(error = "请填写有效的尺码成本与售价") }; return
            }
        }
        _uiState.update { it.copy(isSubmitting = true, error = null) }
        viewModelScope.launch {
            val uploadFile = AtomicReference<File?>()
            try {
                val fields = buildFields(current)
                val imagePart = withContext(Dispatchers.IO) { prepareImage(current.imageUri) { uploadFile.set(it) } }

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
            } catch (e: CancellationException) {
                throw e
            } catch (e: ImagePreparationException) {
                _uiState.update { it.copy(isSubmitting = false, error = e.message ?: "图片读取失败") }
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
            } finally {
                uploadFile.get()?.delete()
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

        if (state.removeImage) put("remove_image", "true")
        if (state.isEditMode && state.productType in listOf("bead", "accessory") && state.initialProduct?.skus?.isNotEmpty() == true) {
            val skus = state.initialProduct.skus
            val defaultId = (skus.firstOrNull { it.is_default } ?: skus.first()).id
            val updated = skus.map { sku ->
                if (sku.id != defaultId) sku else sku.copy(
                    material = state.material, size = state.size.toIntOrNull(), color = state.color,
                    purchase_cost = state.purchaseCost.toDoubleOrNull() ?: 0.0,
                    cost_price = if (state.productType == "bead") (state.purchaseCost.toDoubleOrNull() ?: 0.0) * (state.weight.toDoubleOrNull() ?: 0.0) else state.costPrice.toDoubleOrNull() ?: 0.0,
                    weight = state.weight.toDoubleOrNull() ?: sku.weight,
                    quality_level = state.qualityLevel.toIntOrNull() ?: sku.quality_level,
                    remark = if (state.productType == "bead") state.remark else sku.remark,
                    location = state.location, supplier = state.supplier,
                    selling_price = state.sellingPrice.toDoubleOrNull() ?: 0.0
                )
            }
            put("skus", json.encodeToString(ListSerializer(SkuDto.serializer()), updated))
        }
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
            "children_clothing" -> {
                put("fabric", state.fabric)
                put("size", state.clothingSize)
                put("color", state.color)
                put("season", state.season)
                put("gender", state.gender)
                put("age_range", state.ageRange)
                val items = state.clothingSkus.map { mapOf("size" to it.size.trim().uppercase(), "cost_price" to it.cost, "selling_price" to it.price.ifBlank { "0" }) }
                put("skus", json.encodeToString(kotlinx.serialization.builtins.ListSerializer(kotlinx.serialization.builtins.MapSerializer(kotlinx.serialization.serializer<String>(), kotlinx.serialization.serializer<String>())), items))
            }
            "finished" -> {
                put("cost_mode", state.costMode)
                if (state.manualCost.isNotBlank()) put("manual_cost", state.manualCost)
                put("cost_note", state.costNote)
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

    private class ImagePreparationException(message: String, cause: Throwable) : IOException(message, cause)

    private fun prepareImage(uri: Uri?, onFileCreated: (File) -> Unit): MultipartBody.Part? {
        if (uri == null) return null
        val context = getApplication<Application>()
        val file = try { File.createTempFile("wewin-upload-", ".tmp", context.cacheDir) }
        catch (e: IOException) { throw ImagePreparationException("无法创建图片暂存文件", e) }
        onFileCreated(file)
        try {
            val input = context.contentResolver.openInputStream(uri) ?: throw IOException("无法读取选中的图片")
            input.use { source -> file.outputStream().use { target ->
                val buffer = ByteArray(64 * 1024)
                var size = 0L
                while (true) {
                    val read = source.read(buffer)
                    if (read == -1) break
                    size += read
                    if (size > 100L * 1024 * 1024) throw IOException("图片不能超过100MB")
                    target.write(buffer, 0, read)
                }
                if (size == 0L) throw IOException("图片文件为空")
            } }
            val mime = context.contentResolver.getType(uri) ?: "application/octet-stream"
            val part = MultipartBody.Part.createFormData("image", "upload", file.asRequestBody(mime.toMediaTypeOrNull()))
            return part
        } catch (e: Exception) {
            file.delete()
            throw ImagePreparationException("图片读取失败：${e.message ?: "请重新选择图片"}", e)
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
