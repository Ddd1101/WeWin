package com.wewin.app.ui.products

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.wewin.app.data.remote.dto.AccessoryDto
import com.wewin.app.data.remote.dto.BeadDto
import com.wewin.app.data.remote.dto.FinishedAccessoryItemDto
import com.wewin.app.data.remote.dto.FinishedBeadItemDto
import com.wewin.app.data.remote.dto.FinishedDto
import com.wewin.app.data.remote.dto.ProductDto
import com.wewin.app.data.remote.dto.SkuDto

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductDetailScreen(
    productId: Int,
    onBack: () -> Unit,
    onEdit: (Int) -> Unit,
    viewModel: ProductDetailViewModel = viewModel(
        factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T =
                ProductDetailViewModel(productId) as T
        }
    )
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("商品详情") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "返回"
                        )
                    }
                },
                actions = {
                    val product = uiState.product
                    if (product != null) {
                        IconButton(onClick = { onEdit(product.id) }) {
                            Icon(
                                imageVector = Icons.Filled.Edit,
                                contentDescription = "编辑"
                            )
                        }
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }
                uiState.error != null && uiState.product == null -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = uiState.error ?: "未知错误",
                            color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Spacer(Modifier.height(8.dp))
                        Button(onClick = { viewModel.loadDetail() }) {
                            Text("重试")
                        }
                    }
                }
                uiState.product == null -> {
                    Text(
                        text = "暂无商品信息",
                        modifier = Modifier.align(Alignment.Center),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
                else -> {
                    ProductDetailContent(
                        product = uiState.product!!,
                        error = uiState.error
                    )
                }
            }
        }
    }
}

@Composable
private fun ProductDetailContent(
    product: ProductDto,
    error: String?
) {
    var showSimulate by remember { mutableStateOf(false) }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(
            horizontal = 16.dp,
            vertical = 8.dp
        ),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { ProductImage(imageUrl = product.image_url) }

        if (product.product_type == "finished") {
            item { PriceHeroCard(product = product) }
            item {
                Button(
                    onClick = { showSimulate = true },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = Color(0xFFF59E0B),
                        contentColor = Color.White
                    )
                ) {
                    Text(
                        text = "克价模拟",
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        item { BasicInfoCard(product = product) }

        product.bead?.let { bead ->
            item { BeadInfoCard(bead = bead) }
        }

        product.accessory?.let { accessory ->
            item { AccessoryInfoCard(accessory = accessory) }
        }

        product.finished?.let { finished ->
            item { FinishedInfoCard(finished = finished) }
        }

        if (product.skus.isNotEmpty()) {
            item { SkuListCard(skus = product.skus) }
        }

        if (error != null) {
            item {
                Surface(
                    color = MaterialTheme.colorScheme.errorContainer.copy(alpha = 0.6f),
                    shape = RoundedCornerShape(8.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = error,
                        modifier = Modifier.padding(12.dp),
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        style = MaterialTheme.typography.bodySmall
                    )
                }
            }
        }

        item { Spacer(Modifier.height(16.dp)) }
    }

    if (showSimulate && product.finished != null) {
        SimulateBottomSheet(
            product = product,
            onDismiss = { showSimulate = false }
        )
    }
}

@Composable
private fun ProductImage(imageUrl: String?) {
    val shape = RoundedCornerShape(12.dp)
    if (!imageUrl.isNullOrBlank()) {
        AsyncImage(
            model = imageUrl,
            contentDescription = "商品图片",
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(1f)
                .clip(shape),
            contentScale = ContentScale.Crop
        )
    } else {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(1f)
                .clip(shape)
                .background(MaterialTheme.colorScheme.surfaceVariant),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(
                    imageVector = Icons.Filled.Image,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(48.dp)
                )
                Spacer(Modifier.height(8.dp))
                Text(
                    text = "暂无图片",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

@Composable
private fun PriceHeroCard(product: ProductDto) {
    val profit = product.selling_price - product.cost_price
    val rate = if (product.selling_price > 0) {
        (profit / product.selling_price) * 100
    } else null

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                MetricItem(
                    label = "成本",
                    value = "¥${"%.2f".format(product.cost_price)}",
                    valueColor = MaterialTheme.colorScheme.onSurface,
                    modifier = Modifier.weight(1f)
                )
                MetricItem(
                    label = "售价",
                    value = "¥${"%.2f".format(product.selling_price)}",
                    valueColor = MaterialTheme.colorScheme.error,
                    valueWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
            }
            Spacer(Modifier.height(12.dp))
            HorizontalDivider()
            Spacer(Modifier.height(12.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                MetricItem(
                    label = "利润",
                    value = "¥${"%.2f".format(profit)}",
                    valueColor = if (profit >= 0) Color(0xFF10B981) else MaterialTheme.colorScheme.error,
                    modifier = Modifier.weight(1f)
                )
                MetricItem(
                    label = "利润率",
                    value = if (rate != null) "${"%.1f".format(rate)}%" else "-",
                    valueColor = when {
                        rate == null -> MaterialTheme.colorScheme.onSurface
                        rate >= 30 -> Color(0xFF10B981)
                        rate >= 15 -> Color(0xFFF59E0B)
                        else -> MaterialTheme.colorScheme.error
                    },
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun MetricItem(
    label: String,
    value: String,
    valueColor: Color,
    modifier: Modifier = Modifier,
    valueWeight: FontWeight = FontWeight.SemiBold
) {
    Column(modifier = modifier) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = valueWeight,
            color = valueColor
        )
    }
}

@Composable
private fun BasicInfoCard(product: ProductDto) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = product.code,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                TypeChip(
                    productType = product.product_type,
                    display = product.product_type_display
                )
            }

            ActiveStatusChip(isActive = product.is_active)

            HorizontalDivider()

            InfoRow(label = "商品名称", value = product.name)
            if (product.product_type != "finished") {
                InfoRow(
                    label = "采购成本",
                    value = "¥${"%.2f".format(product.purchase_cost)} /克"
                )
                InfoRow(
                    label = "单颗成本",
                    value = "¥${"%.2f".format(product.cost_price)}"
                )
                InfoRow(
                    label = "售价",
                    value = "¥${"%.2f".format(product.selling_price)}",
                    valueColor = MaterialTheme.colorScheme.error,
                    valueWeight = FontWeight.Bold
                )
            }
            InfoRow(label = "库位", value = product.location)
            InfoRow(label = "供应商", value = product.supplier)
            InfoRow(label = "所属企业", value = product.company_name)
            InfoRow(label = "创建人", value = product.created_by_name)
            InfoRow(label = "创建时间", value = product.created_at?.take(19))
        }
    }
}

@Composable
private fun ActiveStatusChip(isActive: Boolean) {
    val containerColor: Color
    val contentColor: Color
    val text: String
    if (isActive) {
        containerColor = Color(0xFFE8F5E9)
        contentColor = Color(0xFF2E7D32)
        text = "启用"
    } else {
        containerColor = Color(0xFFFFEBEE)
        contentColor = Color(0xFFC62828)
        text = "已停用"
    }
    Surface(
        color = containerColor,
        contentColor = contentColor,
        shape = RoundedCornerShape(50)
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 3.dp),
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
private fun BeadInfoCard(bead: BeadDto) {
    DetailCard(title = "串珠参数") {
        InfoRow(label = "材质", value = bead.material)
        InfoRow(label = "规格", value = bead.size?.toString())
        InfoRow(label = "颜色", value = bead.color)
        InfoRow(
            label = "单颗克重",
            value = "${"%.2f".format(bead.weight)} 克"
        )
        InfoRow(label = "品质等级", value = bead.quality_level.toString())
        InfoRow(label = "备注", value = bead.remark)
    }
}

@Composable
private fun AccessoryInfoCard(accessory: AccessoryDto) {
    DetailCard(title = "配件参数") {
        InfoRow(label = "材质", value = accessory.material)
        InfoRow(label = "规格", value = accessory.size?.toString())
        InfoRow(label = "颜色", value = accessory.color)
    }
}

@Composable
private fun FinishedInfoCard(finished: FinishedDto) {
    DetailCard(title = "成品组成") {
        InfoRow(
            label = "工费",
            value = "¥${"%.2f".format(finished.labor_cost)}"
        )
        InfoRow(
            label = "弹性成本",
            value = "¥${"%.2f".format(finished.elastic_cost)}"
        )

        if (finished.beads.isNotEmpty()) {
            Spacer(Modifier.height(8.dp))
            Text(
                text = "串珠组成",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold
            )
            Spacer(Modifier.height(4.dp))
            finished.beads.forEach { item ->
                FinishedBeadItemRow(item = item)
                Spacer(Modifier.height(4.dp))
            }
        }

        if (finished.accessories.isNotEmpty()) {
            Spacer(Modifier.height(8.dp))
            Text(
                text = "配件组成",
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Bold
            )
            Spacer(Modifier.height(4.dp))
            finished.accessories.forEach { item ->
                FinishedAccessoryItemRow(item = item)
                Spacer(Modifier.height(4.dp))
            }
        }
    }
}

@Composable
private fun FinishedBeadItemRow(item: FinishedBeadItemDto) {
    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
        shape = RoundedCornerShape(10.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Left accent: quantity badge
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = "x${item.quantity}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }

            // Right: name + details
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = item.bead_name ?: "未命名",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold
                )
                item.bead_code?.let {
                    Text(
                        text = "货号 $it",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                    )
                }
                // Price row: 3 items with labels above values
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    CompactMetric(
                        label = "克价",
                        value = item.bead_purchase_cost?.let { "¥${"%.2f".format(it)}/g" } ?: "-",
                        modifier = Modifier.weight(1f)
                    )
                    CompactMetric(
                        label = "单价",
                        value = "¥${"%.2f".format(item.bead_cost_price)}",
                        modifier = Modifier.weight(1f)
                    )
                    CompactMetric(
                        label = "小计",
                        value = "¥${"%.2f".format(item.bead_cost_price * item.quantity)}",
                        modifier = Modifier.weight(1f)
                    )
                }
                item.sku?.let { sku ->
                    Text(
                        text = "SKU：${sku.sku_code ?: "-"}",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                    )
                }
            }
        }
    }
}

@Composable
private fun CompactMetric(
    label: String,
    value: String,
    modifier: Modifier = Modifier,
    valueColor: Color = MaterialTheme.colorScheme.onSurface
) {
    Column(modifier = modifier) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodySmall,
            fontWeight = FontWeight.SemiBold,
            color = valueColor
        )
    }
}

@Composable
private fun FinishedAccessoryItemRow(item: FinishedAccessoryItemDto) {
    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
        shape = RoundedCornerShape(10.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text(
                    text = "x${item.quantity}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = item.accessory_name ?: "未命名",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold
                )
                item.accessory_code?.let {
                    Text(
                        text = "货号 $it",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                    )
                }
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    CompactMetric(
                        label = "成本",
                        value = "¥${"%.2f".format(item.accessory_cost_price)}",
                        modifier = Modifier.weight(1f)
                    )
                    item.sku?.let { sku ->
                        CompactMetric(
                            label = "SKU",
                            value = sku.sku_code ?: "-",
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun SkuListCard(skus: List<SkuDto>) {
    DetailCard(title = "SKU 列表") {
        skus.forEach { sku ->
            SkuItemRow(sku = sku)
            Spacer(Modifier.height(8.dp))
        }
    }
}

@Composable
private fun SkuItemRow(sku: SkuDto) {
    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        shape = RoundedCornerShape(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(10.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = sku.sku_code ?: sku.name ?: "未命名",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                if (sku.is_default) {
                    Surface(
                        color = MaterialTheme.colorScheme.primaryContainer,
                        contentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                        shape = RoundedCornerShape(50)
                    ) {
                        Text(
                            text = "默认",
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp),
                            style = MaterialTheme.typography.labelSmall
                        )
                    }
                }
            }

            val specParts = buildList {
                sku.material?.let { add(it) }
                sku.size?.let { add("${it}mm") }
                sku.color?.let { add(it) }
            }
            if (specParts.isNotEmpty()) {
                Text(
                    text = specParts.joinToString(" / "),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "克重：${"%.2f".format(sku.weight)}g",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "品质：${sku.quality_level}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "成本：¥${"%.2f".format(sku.cost_price)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "售价：¥${"%.2f".format(sku.selling_price)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
private fun DetailCard(
    title: String,
    content: @Composable () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            HorizontalDivider()
            content()
        }
    }
}

@Composable
private fun InfoRow(
    label: String,
    value: String?,
    valueColor: Color = MaterialTheme.colorScheme.onSurface,
    valueWeight: FontWeight = FontWeight.Normal
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.width(88.dp)
        )
        Text(
            text = value?.takeIf { it.isNotBlank() } ?: "-",
            style = MaterialTheme.typography.bodyMedium,
            color = valueColor,
            fontWeight = valueWeight
        )
    }
}

@Composable
private fun HorizontalDivider() {
    androidx.compose.material3.HorizontalDivider(
        color = MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)
    )
}

@Composable
private fun TypeChip(productType: String, display: String?) {
    val containerColor: Color
    val contentColor: Color
    when (productType) {
        "bead" -> {
            containerColor = MaterialTheme.colorScheme.primaryContainer
            contentColor = MaterialTheme.colorScheme.onPrimaryContainer
        }
        "accessory" -> {
            containerColor = MaterialTheme.colorScheme.tertiaryContainer
            contentColor = MaterialTheme.colorScheme.onTertiaryContainer
        }
        "finished" -> {
            containerColor = MaterialTheme.colorScheme.secondaryContainer
            contentColor = MaterialTheme.colorScheme.onSecondaryContainer
        }
        else -> {
            containerColor = MaterialTheme.colorScheme.surfaceVariant
            contentColor = MaterialTheme.colorScheme.onSurfaceVariant
        }
    }
    Surface(
        color = containerColor,
        contentColor = contentColor,
        shape = RoundedCornerShape(50)
    ) {
        Text(
            text = display ?: productType,
            modifier = Modifier.padding(horizontal = 10.dp, vertical = 3.dp),
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Bold
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun SimulateBottomSheet(
    product: ProductDto,
    onDismiss: () -> Unit
) {
    val finished = product.finished ?: return
    val beads = finished.beads
    val accessories = finished.accessories
    val sheetState = rememberModalBottomSheetState()

    val beadNewPrices = remember {
        mutableStateMapOf<Int, String>().apply {
            beads.forEach { b ->
                put(b.bead_id, "%.2f".format(b.bead_purchase_cost ?: 0.0))
            }
        }
    }
    val accessoryNewPrices = remember {
        mutableStateMapOf<Int, String>().apply {
            accessories.forEach { a ->
                put(a.accessory_id, "%.2f".format(a.accessory_cost_price))
            }
        }
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp)
                .padding(bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Header: 标题 + 商品信息紧凑展示
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "克价模拟",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )
                Surface(
                    color = Color(0xFFEF4444).copy(alpha = 0.1f),
                    shape = RoundedCornerShape(50)
                ) {
                    Text(
                        text = "售价 ¥${"%.2f".format(product.selling_price)}",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFEF4444),
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                    )
                }
            }

            val originalCost = beads.sumOf { it.bead_cost_price * it.quantity } +
                accessories.sumOf { it.accessory_cost_price * it.quantity } +
                finished.labor_cost + finished.elastic_cost

            var newCost = 0.0
            beads.forEach { b ->
                val newPrice = beadNewPrices[b.bead_id]?.toDoubleOrNull() ?: 0.0
                newCost += newPrice * b.bead_weight * b.quantity
            }
            accessories.forEach { a ->
                val newPrice = accessoryNewPrices[a.accessory_id]?.toDoubleOrNull() ?: 0.0
                newCost += newPrice * a.quantity
            }
            newCost += finished.labor_cost + finished.elastic_cost

            // 明细区
            if (beads.isNotEmpty()) {
                SectionHeader(
                    title = "串珠",
                    count = beads.size,
                    totalQuantity = beads.sumOf { it.quantity },
                    unit = "颗"
                )
                beads.forEach { bead ->
                    SimulateBeadRow(
                        bead = bead,
                        newPriceText = beadNewPrices[bead.bead_id] ?: "",
                        onNewPriceChange = { beadNewPrices[bead.bead_id] = it }
                    )
                }
            }

            if (accessories.isNotEmpty()) {
                SectionHeader(
                    title = "配件",
                    count = accessories.size,
                    totalQuantity = accessories.sumOf { it.quantity },
                    unit = "个"
                )
                accessories.forEach { acc ->
                    SimulateAccessoryRow(
                        accessory = acc,
                        newPriceText = accessoryNewPrices[acc.accessory_id] ?: "",
                        onNewPriceChange = { accessoryNewPrices[acc.accessory_id] = it }
                    )
                }
            }

            if (beads.isEmpty() && accessories.isEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 24.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = "无明细",
                        style = MaterialTheme.typography.bodyLarge,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // 汇总区: 深色 hero 卡片
            SimulateSummary(
                originalCost = originalCost,
                newCost = newCost,
                sellingPrice = product.selling_price
            )

            // 底部按钮
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                TextButton(
                    onClick = {
                        beads.forEach { b ->
                            beadNewPrices[b.bead_id] = "%.2f".format(b.bead_purchase_cost ?: 0.0)
                        }
                        accessories.forEach { a ->
                            accessoryNewPrices[a.accessory_id] = "%.2f".format(a.accessory_cost_price)
                        }
                    },
                    modifier = Modifier.weight(1f)
                ) {
                    Text("重置")
                }
                Button(
                    onClick = onDismiss,
                    modifier = Modifier.weight(1f)
                ) {
                    Text("关闭")
                }
            }
        }
    }
}

@Composable
private fun SectionHeader(
    title: String,
    count: Int,
    totalQuantity: Int,
    unit: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.Bottom,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = "$count 种 · 共 $totalQuantity $unit",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun SimulateBeadRow(
    bead: FinishedBeadItemDto,
    newPriceText: String,
    onNewPriceChange: (String) -> Unit
) {
    val newPrice = newPriceText.toDoubleOrNull() ?: 0.0
    val originalSubtotal = bead.bead_cost_price * bead.quantity
    val newSubtotal = newPrice * bead.bead_weight * bead.quantity
    val delta = newSubtotal - originalSubtotal
    val deltaColor = if (delta > 0) Color(0xFFEF4444) else Color(0xFF10B981)

    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(
            1.dp,
            MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)
        ),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            // 顶部: 名称 + 数量徽章
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = bead.bead_name ?: "未命名",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                Surface(
                    color = MaterialTheme.colorScheme.primaryContainer,
                    shape = RoundedCornerShape(50)
                ) {
                    Text(
                        text = "x${bead.quantity}",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                    )
                }
            }

            // 中部: 原克价 → 新克价输入
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "原 ¥${"%.2f".format(bead.bead_purchase_cost ?: 0.0)}/g",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.width(90.dp)
                )
                OutlinedTextField(
                    value = newPriceText,
                    onValueChange = onNewPriceChange,
                    label = { Text("新克价/g") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    singleLine = true,
                    modifier = Modifier.weight(1f)
                )
                // 快捷调整按钮
                FilledIconButton(
                    onClick = {
                        val current = newPriceText.toDoubleOrNull() ?: 0.0
                        onNewPriceChange("%.2f".format((current - 0.1).coerceAtLeast(0.0)))
                    },
                    shape = CircleShape,
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    ),
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(
                        imageVector = Icons.Filled.Remove,
                        contentDescription = "减少 0.1",
                        modifier = Modifier.size(18.dp)
                    )
                }
                FilledIconButton(
                    onClick = {
                        val current = newPriceText.toDoubleOrNull() ?: 0.0
                        onNewPriceChange("%.2f".format(current + 0.1))
                    },
                    shape = CircleShape,
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    ),
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(
                        imageVector = Icons.Filled.Add,
                        contentDescription = "增加 0.1",
                        modifier = Modifier.size(18.dp)
                    )
                }
            }

            // 底部: 新小计 hero
            Surface(
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "新小计",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "¥${"%.2f".format(newSubtotal)}",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = deltaColor
                        )
                        if (delta != 0.0) {
                            Text(
                                text = "${if (delta > 0) "+" else ""}¥${"%.2f".format(delta)}",
                                style = MaterialTheme.typography.labelSmall,
                                color = deltaColor
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SimulateAccessoryRow(
    accessory: FinishedAccessoryItemDto,
    newPriceText: String,
    onNewPriceChange: (String) -> Unit
) {
    val newPrice = newPriceText.toDoubleOrNull() ?: 0.0
    val originalSubtotal = accessory.accessory_cost_price * accessory.quantity
    val newSubtotal = newPrice * accessory.quantity
    val delta = newSubtotal - originalSubtotal
    val deltaColor = if (delta > 0) Color(0xFFEF4444) else Color(0xFF10B981)

    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(12.dp),
        border = androidx.compose.foundation.BorderStroke(
            1.dp,
            MaterialTheme.colorScheme.outlineVariant.copy(alpha = 0.5f)
        ),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(14.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            // 顶部: 名称 + 数量徽章
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = accessory.accessory_name ?: "未命名",
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.weight(1f)
                )
                Surface(
                    color = MaterialTheme.colorScheme.tertiaryContainer,
                    shape = RoundedCornerShape(50)
                ) {
                    Text(
                        text = "x${accessory.quantity}",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onTertiaryContainer,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 2.dp)
                    )
                }
            }

            // 中部: 原单价 → 新单价输入
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "原 ¥${"%.2f".format(accessory.accessory_cost_price)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.width(90.dp)
                )
                OutlinedTextField(
                    value = newPriceText,
                    onValueChange = onNewPriceChange,
                    label = { Text("新单价") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
                    singleLine = true,
                    modifier = Modifier.weight(1f)
                )
                FilledIconButton(
                    onClick = {
                        val current = newPriceText.toDoubleOrNull() ?: 0.0
                        onNewPriceChange("%.2f".format((current - 0.1).coerceAtLeast(0.0)))
                    },
                    shape = CircleShape,
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    ),
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(
                        imageVector = Icons.Filled.Remove,
                        contentDescription = "减少 0.1",
                        modifier = Modifier.size(18.dp)
                    )
                }
                FilledIconButton(
                    onClick = {
                        val current = newPriceText.toDoubleOrNull() ?: 0.0
                        onNewPriceChange("%.2f".format(current + 0.1))
                    },
                    shape = CircleShape,
                    colors = IconButtonDefaults.filledIconButtonColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    ),
                    modifier = Modifier.size(36.dp)
                ) {
                    Icon(
                        imageVector = Icons.Filled.Add,
                        contentDescription = "增加 0.1",
                        modifier = Modifier.size(18.dp)
                    )
                }
            }

            // 底部: 新小计 hero
            Surface(
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "新小计",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "¥${"%.2f".format(newSubtotal)}",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = deltaColor
                        )
                        if (delta != 0.0) {
                            Text(
                                text = "${if (delta > 0) "+" else ""}¥${"%.2f".format(delta)}",
                                style = MaterialTheme.typography.labelSmall,
                                color = deltaColor
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SimulateSummary(
    originalCost: Double,
    newCost: Double,
    sellingPrice: Double
) {
    val costChange = newCost - originalCost
    val originalProfit = sellingPrice - originalCost
    val newProfit = sellingPrice - newCost
    val originalProfitRate = if (sellingPrice > 0) (originalProfit / sellingPrice) * 100 else 0.0
    val newProfitRate = if (sellingPrice > 0) (newProfit / sellingPrice) * 100 else 0.0

    val costColor = if (newCost > originalCost) Color(0xFFFCA5A5) else Color(0xFF86EFAC)
    val newProfitColor = if (newProfit >= 0) Color(0xFF86EFAC) else Color(0xFFFCA5A5)
    val newProfitRateColor = when {
        newProfitRate >= 30 -> Color(0xFF86EFAC)
        newProfitRate >= 15 -> Color(0xFFFCD34D)
        else -> Color(0xFFFCA5A5)
    }

    // 深色 hero 卡片
    Surface(
        color = Color(0xFF1E293B),
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // 核心: 新利润率超大字
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "新利润率",
                        style = MaterialTheme.typography.labelMedium,
                        color = Color(0xFF94A3B8)
                    )
                    Text(
                        text = "原 ${"%.1f".format(originalProfitRate)}%",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color(0xFF64748B)
                    )
                }
                Text(
                    text = "${"%.1f".format(newProfitRate)}%",
                    style = MaterialTheme.typography.displaySmall,
                    fontWeight = FontWeight.Bold,
                    color = newProfitRateColor
                )
            }

            // 分隔线
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(1.dp)
                    .background(Color(0xFF334155))
            )

            // 次要指标网格
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                SummaryMetricDark(
                    label = "新成本",
                    value = "¥${"%.2f".format(newCost)}",
                    subValue = "原 ¥${"%.2f".format(originalCost)}",
                    valueColor = costColor,
                    modifier = Modifier.weight(1f)
                )
                SummaryMetricDark(
                    label = "成本变动",
                    value = "${if (costChange > 0) "+" else ""}¥${"%.2f".format(costChange)}",
                    subValue = if (costChange == 0.0) "持平" else if (costChange > 0) "上升" else "下降",
                    valueColor = costColor,
                    modifier = Modifier.weight(1f)
                )
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                SummaryMetricDark(
                    label = "新利润",
                    value = "¥${"%.2f".format(newProfit)}",
                    subValue = "原 ¥${"%.2f".format(originalProfit)}",
                    valueColor = newProfitColor,
                    modifier = Modifier.weight(1f)
                )
                SummaryMetricDark(
                    label = "售价",
                    value = "¥${"%.2f".format(sellingPrice)}",
                    subValue = "固定",
                    valueColor = Color(0xFFFCA5A5),
                    modifier = Modifier.weight(1f)
                )
            }
        }
    }
}

@Composable
private fun SummaryMetricDark(
    label: String,
    value: String,
    subValue: String,
    valueColor: Color,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(2.dp)
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = Color(0xFF94A3B8)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = valueColor
        )
        Text(
            text = subValue,
            style = MaterialTheme.typography.labelSmall,
            color = Color(0xFF64748B)
        )
    }
}
