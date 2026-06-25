package com.wewin.app.ui.products

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.wewin.app.data.remote.RetrofitClient
import com.wewin.app.data.remote.dto.ErrorResponse
import com.wewin.app.data.remote.dto.ProductDto
import com.wewin.app.data.remote.dto.ProductStatsDto.ProductStats
import com.wewin.app.data.remote.dto.SkuDto
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import java.io.IOException

sealed interface SkuLoadState {
    object Idle : SkuLoadState
    object Loading : SkuLoadState
    data class Success(val skus: List<SkuDto>) : SkuLoadState
    data class Error(val message: String) : SkuLoadState
}

data class ProductListUiState(
    val products: List<ProductDto> = emptyList(),
    val stats: ProductStats? = null,
    val isLoading: Boolean = false,
    val isLoadingMore: Boolean = false,
    val error: String? = null,
    val selectedType: String? = null,
    val searchKeyword: String = "",
    val page: Int = 1,
    val totalCount: Int = 0,
    val hasMore: Boolean = true,
    val isRefreshing: Boolean = false,
    val skuMap: Map<Int, SkuLoadState> = emptyMap()
)

class ProductListViewModel : ViewModel() {

    private val apiService = RetrofitClient.apiService

    private val pageSize: Int = 50

    private val _uiState = MutableStateFlow(ProductListUiState())
    val uiState: StateFlow<ProductListUiState> = _uiState.asStateFlow()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
    }

    init {
        loadInitial()
    }

    fun loadInitial() {
        val current = _uiState.value
        if (current.isLoading) return
        val selectedType = current.selectedType
        _uiState.update {
            it.copy(
                isLoading = true,
                error = null,
                page = 1,
                hasMore = true,
                products = emptyList()
            )
        }
        viewModelScope.launch {
            try {
                coroutineScope {
                    val listDeferred = async {
                        apiService.getProducts(
                            productType = selectedType,
                            page = 1,
                            pageSize = pageSize
                        )
                    }
                    val statsDeferred = async { apiService.getProductStats() }

                    val listResponse = listDeferred.await()
                    val statsResponse = statsDeferred.await()

                    if (listResponse.isSuccessful) {
                        val body = listResponse.body()
                        val products = body?.products ?: emptyList()
                        val totalCount = body?.total_count ?: 0
                        val newHasMore = pageSize < totalCount
                        val stats = if (statsResponse.isSuccessful) {
                            statsResponse.body()?.product_stats
                        } else {
                            null
                        }
                        _uiState.update {
                            it.copy(
                                products = products,
                                totalCount = totalCount,
                                page = 1,
                                hasMore = newHasMore,
                                stats = stats,
                                isLoading = false,
                                isRefreshing = false,
                                error = null
                            )
                        }
                    } else {
                        val errorMsg = parseError(
                            listResponse.code(),
                            listResponse.errorBody()?.string()
                        )
                        _uiState.update {
                            it.copy(
                                isLoading = false,
                                isRefreshing = false,
                                error = errorMsg
                            )
                        }
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        isRefreshing = false,
                        error = "网络连接失败，请检查网络"
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoading = false,
                        isRefreshing = false,
                        error = "加载失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    fun loadMore() {
        val current = _uiState.value
        if (current.isLoadingMore || !current.hasMore) return
        val nextPage = current.page + 1
        val selectedType = current.selectedType
        _uiState.update { it.copy(isLoadingMore = true) }
        viewModelScope.launch {
            try {
                val response = apiService.getProducts(
                    productType = selectedType,
                    page = nextPage,
                    pageSize = pageSize
                )
                if (response.isSuccessful) {
                    val body = response.body()
                    val newProducts = body?.products ?: emptyList()
                    val totalCount = body?.total_count ?: current.totalCount
                    val merged = current.products + newProducts
                    val newHasMore = (nextPage * pageSize) < totalCount
                    _uiState.update {
                        it.copy(
                            products = merged,
                            page = nextPage,
                            totalCount = totalCount,
                            hasMore = newHasMore,
                            isLoadingMore = false,
                            error = null
                        )
                    }
                } else {
                    val errorMsg = parseError(
                        response.code(),
                        response.errorBody()?.string()
                    )
                    _uiState.update {
                        it.copy(isLoadingMore = false, error = errorMsg)
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(isLoadingMore = false, error = "网络连接失败，请检查网络")
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        isLoadingMore = false,
                        error = "加载失败：${e.message ?: "未知错误"}"
                    )
                }
            }
        }
    }

    fun refresh() {
        val current = _uiState.value
        if (current.isLoading) return
        _uiState.update { it.copy(isRefreshing = true) }
        loadInitial()
    }

    fun selectType(type: String?) {
        val current = _uiState.value
        if (current.selectedType == type) return
        _uiState.update { it.copy(selectedType = type) }
        loadInitial()
    }

    fun updateKeyword(keyword: String) {
        _uiState.update { it.copy(searchKeyword = keyword) }
    }

    fun search() {
        loadInitial()
    }

    fun loadSkusIfNeeded(productId: Int, existingSkus: List<SkuDto>) {
        if (existingSkus.isNotEmpty()) {
            val current = _uiState.value.skuMap[productId]
            if (current !is SkuLoadState.Success) {
                _uiState.update {
                    it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Success(existingSkus)))
                }
            }
            return
        }
        val state = _uiState.value.skuMap[productId]
        if (state is SkuLoadState.Loading || state is SkuLoadState.Success) return
        _uiState.update {
            it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Loading))
        }
        viewModelScope.launch {
            try {
                val response = apiService.getProductSkus(productId)
                if (response.isSuccessful) {
                    val skus = response.body()?.skus ?: emptyList()
                    _uiState.update {
                        it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Success(skus)))
                    }
                } else {
                    val errorMsg = parseError(
                        response.code(),
                        response.errorBody()?.string()
                    )
                    _uiState.update {
                        it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Error(errorMsg)))
                    }
                }
            } catch (e: IOException) {
                _uiState.update {
                    it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Error("网络连接失败，请检查网络")))
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(skuMap = it.skuMap + (productId to SkuLoadState.Error("加载失败：${e.message ?: "未知错误"}")))
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
            404 -> "接口不存在"
            in 500..599 -> "服务器错误，请稍后重试"
            else -> "请求失败（$code）"
        }
    }
}
