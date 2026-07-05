package com.wewin.app.data.remote

import com.wewin.app.data.remote.dto.AccessoryListDto
import com.wewin.app.data.remote.dto.BeadListDto
import com.wewin.app.data.remote.dto.CarryOverResponse
import com.wewin.app.data.remote.dto.CreatePurchaseItemRequest
import com.wewin.app.data.remote.dto.CreatePurchaseListRequest
import com.wewin.app.data.remote.dto.LoginRequest
import com.wewin.app.data.remote.dto.LoginResponse
import com.wewin.app.data.remote.dto.MarkPartialRequest
import com.wewin.app.data.remote.dto.MessageResponse
import com.wewin.app.data.remote.dto.ProductDto
import com.wewin.app.data.remote.dto.ProductListResponse
import com.wewin.app.data.remote.dto.ProductStatsDto
import com.wewin.app.data.remote.dto.ProductTypesDto
import com.wewin.app.data.remote.dto.PurchaseItemResponse
import com.wewin.app.data.remote.dto.PurchaseListDto
import com.wewin.app.data.remote.dto.PurchaseListResponse
import com.wewin.app.data.remote.dto.SkuListResponse
import com.wewin.app.data.remote.dto.UncompletedListsResponse
import com.wewin.app.data.remote.dto.UpdatePurchaseListRequest
import com.wewin.app.data.remote.dto.UserListResponse
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Part
import retrofit2.http.PartMap
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {

    @POST("api/account/login/")
    suspend fun login(@Body body: LoginRequest): Response<LoginResponse>

    @GET("api/store/products/types/")
    suspend fun getProductTypes(): Response<ProductTypesDto>

    @GET("api/store/products/stats/")
    suspend fun getProductStats(): Response<ProductStatsDto>

    @GET("api/store/products/")
    suspend fun getProducts(
        @Query("product_type") productType: String? = null,
        @Query("is_active") isActive: String? = null,
        @Query("ordering") ordering: String? = null,
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 50
    ): Response<ProductListResponse>

    @GET("api/store/products/{id}/detail/")
    suspend fun getProductDetail(@Path("id") id: Int): Response<ProductDto>

    @GET("api/store/products/beads/")
    suspend fun getBeads(): Response<BeadListDto>

    @GET("api/store/products/accessories/")
    suspend fun getAccessories(): Response<AccessoryListDto>

    @GET("api/store/products/{id}/skus/")
    suspend fun getProductSkus(@Path("id") id: Int): Response<SkuListResponse>

    @Multipart
    @POST("api/store/products/create/")
    suspend fun createProductMultipart(
        @PartMap fields: Map<String, @JvmSuppressWildcards RequestBody>,
        @Part image: MultipartBody.Part? = null
    ): Response<ProductDto>

    @Multipart
    @PUT("api/store/products/{id}/update/")
    suspend fun updateProductMultipart(
        @Path("id") id: Int,
        @PartMap fields: Map<String, @JvmSuppressWildcards RequestBody>,
        @Part image: MultipartBody.Part? = null
    ): Response<ProductDto>

    @DELETE("api/store/products/{id}/delete/")
    suspend fun deleteProduct(@Path("id") id: Int): Response<MessageResponse>

    // ===== 用户列表（采购指派人选择） =====
    @GET("api/account/users/")
    suspend fun getUsers(): Response<UserListResponse>

    // ===== 采购清单 =====
    @GET("api/purchase/lists/")
    suspend fun getPurchaseLists(
        @Query("status") status: String? = null,
        @Query("assignee_scope") assigneeScope: String = "my_assigned",
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 50
    ): Response<PurchaseListResponse>

    @POST("api/purchase/lists/create/")
    suspend fun createPurchaseList(
        @Body request: CreatePurchaseListRequest
    ): Response<PurchaseListDto>

    @GET("api/purchase/lists/{id}/")
    suspend fun getPurchaseListDetail(
        @Path("id") id: Int
    ): Response<PurchaseListDto>

    @PUT("api/purchase/lists/{id}/update/")
    suspend fun updatePurchaseList(
        @Path("id") id: Int,
        @Body request: UpdatePurchaseListRequest
    ): Response<PurchaseListDto>

    @GET("api/purchase/lists/uncompleted/")
    suspend fun getUncompletedLists(): Response<UncompletedListsResponse>

    @POST("api/purchase/lists/{id}/items/add/")
    suspend fun addPurchaseItem(
        @Path("id") listId: Int,
        @Body request: CreatePurchaseItemRequest
    ): Response<PurchaseListDto>

    // ===== 采购项状态操作 =====
    @POST("api/purchase/items/{id}/mark-purchased/")
    suspend fun markItemPurchased(
        @Path("id") itemId: Int
    ): Response<PurchaseItemResponse>

    @POST("api/purchase/items/{id}/mark-partial/")
    suspend fun markItemPartial(
        @Path("id") itemId: Int,
        @Body request: MarkPartialRequest
    ): Response<PurchaseItemResponse>

    @POST("api/purchase/items/{id}/carry-over-next-day/")
    suspend fun carryOverNextDay(
        @Path("id") itemId: Int
    ): Response<CarryOverResponse>
}
