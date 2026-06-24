package com.wewin.app.ui.products

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.wewin.app.data.remote.RetrofitClient
import com.wewin.app.data.remote.dto.ErrorResponse
import com.wewin.app.data.remote.dto.ProductDto
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import java.io.IOException

data class ProductDetailUiState(
    val product: ProductDto? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val isDeleting: Boolean = false,
    val deleteSuccess: Boolean = false
)

class ProductDetailViewModel(
    private val productId: Int
) : ViewModel() {

    private val apiService = RetrofitClient.apiService

    private val _uiState = MutableStateFlow(ProductDetailUiState())
    val uiState: StateFlow<ProductDetailUiState> = _uiState.asStateFlow()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    init {
        loadDetail()
    }

    fun loadDetail() {
        val current = _uiState.value
        if (current.isLoading) return
        _uiState.update { it.copy(isLoading = true, error = null) }
        viewModelScope.launch {
            try {
                val response = apiService.getProductDetail(productId)
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body != null) {
                        _uiState.update {
                            it.copy(isLoading = false, product = body, error = null)
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

    fun deleteProduct() {
        val current = _uiState.value
        if (current.isDeleting) return
        _uiState.update { it.copy(isDeleting = true, error = null) }
        viewModelScope.launch {
            try {
                val response = apiService.deleteProduct(productId)
                if (response.isSuccessful) {
                    _uiState.update {
                        it.copy(isDeleting = false, deleteSuccess = true)
                    }
                } else {
                    val errorMsg = parseError(response.code(), response.errorBody()?.string())
                    _uiState.update { it.copy(isDeleting = false, error = errorMsg) }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(isDeleting = false, error = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isDeleting = false,
                        error = "删除失败：${e.message ?: "未知错误"}"
                    )
                }
            }
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
