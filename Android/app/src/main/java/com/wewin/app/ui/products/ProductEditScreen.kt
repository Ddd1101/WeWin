package com.wewin.app.ui.products

import android.app.Application
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Image
import androidx.compose.material3.Button
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Switch
import androidx.compose.material3.TextButton
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.horizontalScroll
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import androidx.compose.ui.res.painterResource
import com.wewin.app.R

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductEditScreen(
    productId: Int?,
    onBack: () -> Unit
) {
    val context = LocalContext.current
    val viewModel: ProductEditViewModel = viewModel(
        factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T =
                ProductEditViewModel(
                    productId,
                    context.applicationContext as Application
                ) as T
        }
    )
    val uiState by viewModel.uiState.collectAsState()
    val focusManager = LocalFocusManager.current
    val keyboard = LocalSoftwareKeyboardController.current
    val submit = { focusManager.clearFocus(); keyboard?.hide(); viewModel.submit() }

    val imagePicker = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.PickVisualMedia()
    ) { uri: Uri? ->
        if (uri != null) viewModel.setImageUri(uri)
    }

    LaunchedEffect(uiState.submitSuccess) {
        if (uiState.submitSuccess) {
            onBack()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (uiState.isEditMode) "编辑商品" else "新建商品") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "返回"
                        )
                    }
                },
                actions = {
                    IconButton(
                        onClick = submit,
                        enabled = !uiState.isSubmitting && !uiState.isLoading
                    ) {
                        if (uiState.isSubmitting) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(20.dp),
                                strokeWidth = 2.dp
                            )
                        } else {
                            Icon(
                                imageVector = Icons.Filled.Check,
                                contentDescription = "保存"
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
            if (uiState.isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
            } else {
                ProductEditContent(
                    uiState = uiState,
                    onPickImage = {
                        imagePicker.launch(
                            PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
                        )
                    },
                    onSubmit = submit,
                    onChange = viewModel::updateForm,
                    onRemoveImage = viewModel::removeImage,
                    onReloadMaterials = viewModel::loadFinishedOptions
                )
            }
        }
    }
}

@Composable
private fun ProductEditContent(
    uiState: ProductEditUiState,
    onPickImage: () -> Unit,
    onSubmit: () -> Unit,
    onChange: ((ProductEditUiState) -> ProductEditUiState) -> Unit,
    onRemoveImage: () -> Unit,
    onReloadMaterials: () -> Unit
) {
    val scrollState = rememberLazyListState()
    LaunchedEffect(uiState.error) { if (uiState.error != null) scrollState.animateScrollToItem(0) }
    LazyColumn(
        state = scrollState,
        modifier = Modifier.fillMaxSize().imePadding(),
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        if (uiState.error != null) item { ErrorBanner(error = uiState.error) }
        item {
            ImagePickerSection(uiState = uiState, onPickImage = onPickImage)
            if (uiState.imageUri != null || (!uiState.removeImage && !uiState.initialProduct?.image_url.isNullOrBlank())) {
                TextButton(onClick = onRemoveImage, enabled = !uiState.isSubmitting) { Text("移除图片") }
            }
        }
        item { Text("基本信息", style = MaterialTheme.typography.titleMedium) }
        item { EditField("货号", uiState.code, enabled = !uiState.isEditMode && !uiState.isSubmitting) { value -> onChange { it.copy(code = value) } } }
        item { EditField("商品名称", uiState.name, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(name = value) } } }
        item {
            Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("bead" to "串珠", "accessory" to "配件", "finished" to "成品", "children_clothing" to "童装").forEach { (type, label) ->
                    FilterChip(selected = uiState.productType == type, enabled = !uiState.isEditMode && !uiState.isSubmitting,
                        onClick = { onChange { it.copy(productType = type) } }, label = { Text(label) })
                }
            }
        }
        item { EditField("供应商", uiState.supplier, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(supplier = value) } } }
        item { EditField("库位", uiState.location, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(location = value) } } }
        item { EditField("采购成本", uiState.purchaseCost, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(purchaseCost = value) } } }
        if (uiState.productType == "accessory") item { EditField("成本价格", uiState.costPrice, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(costPrice = value) } } }
        if (uiState.productType == "finished") item { Text("成品成本按组成与工费计算，保存后更新。", style = MaterialTheme.typography.bodySmall) }
        if (uiState.productType == "children_clothing") item { Text("商品成本取最低尺码成本。", style = MaterialTheme.typography.bodySmall) }
        item { EditField("售卖价格", uiState.sellingPrice, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(sellingPrice = value) } } }
        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text("启用商品")
                Switch(checked = uiState.isActive, enabled = !uiState.isSubmitting, onCheckedChange = { value -> onChange { it.copy(isActive = value) } })
            }
        }
        if (uiState.productType in listOf("bead", "accessory")) {
            item { Text("材料信息", style = MaterialTheme.typography.titleMedium) }
            item { EditField("材质", uiState.material, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(material = value) } } }
            item { EditField("规格(mm)", uiState.size, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(size = value) } } }
            item { EditField("颜色", uiState.color, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(color = value) } } }
            if (uiState.productType == "bead") {
                item { EditField("克重(g)", uiState.weight, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(weight = value) } } }
                item { EditField("品质等级(1-10)", uiState.qualityLevel, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(qualityLevel = value) } } }
                item { EditField("备注", uiState.remark, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(remark = value) } } }
            }
            if ((uiState.initialProduct?.skus?.size ?: 0) > 1) item { Text("基本信息修改同步默认SKU，其他SKU保留原数据。", style = MaterialTheme.typography.bodySmall) }
        }
        if (uiState.productType == "children_clothing") {
            item { Text("童装信息与尺码成本", style = MaterialTheme.typography.titleMedium) }
            item { EditField("面料", uiState.fabric, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(fabric = value) } } }
            item { EditField("尺码描述", uiState.clothingSize, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(clothingSize = value) } } }
            item { EditField("颜色", uiState.color, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(color = value) } } }
            item { EditField("季节", uiState.season, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(season = value) } } }
            item { EditField("适用性别", uiState.gender, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(gender = value) } } }
            item { EditField("年龄段", uiState.ageRange, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(ageRange = value) } } }
            uiState.clothingSkus.forEachIndexed { index, sku ->
                item {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        EditField("尺码 ${index + 1}", sku.size, enabled = !uiState.isSubmitting) { value -> onChange { state -> state.copy(clothingSkus = state.clothingSkus.mapIndexed { i, row -> if (i == index) row.copy(size = value) else row }) } }
                        EditField("尺码成本 ${index + 1}", sku.cost, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { state -> state.copy(clothingSkus = state.clothingSkus.mapIndexed { i, row -> if (i == index) row.copy(cost = value) else row }) } }
                        EditField("尺码售价 ${index + 1}", sku.price, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { state -> state.copy(clothingSkus = state.clothingSkus.mapIndexed { i, row -> if (i == index) row.copy(price = value) else row }) } }
                        TextButton(enabled = !uiState.isSubmitting, onClick = { onChange { state -> state.copy(clothingSkus = state.clothingSkus.filterIndexed { i, _ -> i != index }) } }) { Text("删除尺码 ${index + 1}") }
                    }
                }
            }
            item { Button(enabled = !uiState.isSubmitting, onClick = { onChange { it.copy(clothingSkus = it.clothingSkus + ClothingSkuInput()) } }) { Text("添加尺码") } }
        }
        if (uiState.productType == "finished") {
            item { EditField("工费", uiState.laborCost, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(laborCost = value) } } }
            item { EditField("弹力线成本", uiState.elasticCost, numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { it.copy(elasticCost = value) } } }
            item { TextButton(onClick = onReloadMaterials, enabled = !uiState.isSubmitting) { Text("刷新材料") } }
            uiState.beadComponents.forEachIndexed { index, component ->
                item {
                    val options = uiState.beadOptions.flatMap { material ->
                        if (material.skus.isEmpty()) listOf(MaterialChoice(material.id, null, "${material.code} ${material.name}"))
                        else material.skus.map { MaterialChoice(material.id, it.id, "${material.code} / ${it.name ?: it.sku_code} / ¥${it.cost_price}") }
                    }
                    MaterialPicker("串珠 ${index + 1}", options, component.beadId, component.skuId, !uiState.isSubmitting) { option -> onChange { state -> state.copy(beadComponents = state.beadComponents.mapIndexed { i, old -> if (i == index) old.copy(beadId = option.id, skuId = option.skuId) else old }) } }
                    EditField("串珠数量 ${index + 1}", component.quantity.toString(), numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { state -> state.copy(beadComponents = state.beadComponents.mapIndexed { i, old -> if (i == index) old.copy(quantity = value.toIntOrNull() ?: 0) else old }) } }
                    TextButton(onClick = { onChange { state -> state.copy(beadComponents = state.beadComponents.filterIndexed { i, _ -> i != index }) } }) { Text("移除串珠 ${index + 1}") }
                }
            }
            item { Button(onClick = { onChange { it.copy(beadComponents = it.beadComponents + BeadComponent()) } }, enabled = !uiState.isSubmitting) { Text("添加串珠") } }
            uiState.accessoryComponents.forEachIndexed { index, component ->
                item {
                    val options = uiState.accessoryOptions.flatMap { material ->
                        if (material.skus.isEmpty()) listOf(MaterialChoice(material.id, null, "${material.code} ${material.name}"))
                        else material.skus.map { MaterialChoice(material.id, it.id, "${material.code} / ${it.name ?: it.sku_code} / ¥${it.cost_price}") }
                    }
                    MaterialPicker("配件 ${index + 1}", options, component.accessoryId, component.skuId, !uiState.isSubmitting) { option -> onChange { state -> state.copy(accessoryComponents = state.accessoryComponents.mapIndexed { i, old -> if (i == index) old.copy(accessoryId = option.id, skuId = option.skuId) else old }) } }
                    EditField("配件数量 ${index + 1}", component.quantity.toString(), numeric = true, enabled = !uiState.isSubmitting) { value -> onChange { state -> state.copy(accessoryComponents = state.accessoryComponents.mapIndexed { i, old -> if (i == index) old.copy(quantity = value.toIntOrNull() ?: 0) else old }) } }
                    TextButton(onClick = { onChange { state -> state.copy(accessoryComponents = state.accessoryComponents.filterIndexed { i, _ -> i != index }) } }) { Text("移除配件 ${index + 1}") }
                }
            }
            item { Button(onClick = { onChange { it.copy(accessoryComponents = it.accessoryComponents + AccessoryComponent()) } }, enabled = !uiState.isSubmitting) { Text("添加配件") } }
        }


        item {
            Button(
                onClick = onSubmit,
                modifier = Modifier.fillMaxWidth(),
                enabled = !uiState.isSubmitting
            ) {
                if (uiState.isSubmitting) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(18.dp),
                        strokeWidth = 2.dp,
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Text("保存")
                }
            }
        }

        item { Spacer(Modifier.height(16.dp)) }
    }
}

@Composable
private fun ImagePickerSection(
    uiState: ProductEditUiState,
    onPickImage: () -> Unit
) {
    val shape = RoundedCornerShape(12.dp)
    val displayUri = uiState.imageUri
    val displayUrl = if (uiState.removeImage) null else uiState.initialProduct?.image_url

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(1.8f)
            .clip(shape)
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clickable(enabled = !uiState.isSubmitting) { onPickImage() },
        contentAlignment = Alignment.Center
    ) {
        if (displayUri != null) {
            AsyncImage(
            placeholder = painterResource(R.drawable.ic_image_placeholder),
            error = painterResource(R.drawable.ic_image_placeholder),
                model = displayUri,
                contentDescription = "商品图片",
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop
            )
        } else if (!displayUrl.isNullOrBlank()) {
            AsyncImage(
            placeholder = painterResource(R.drawable.ic_image_placeholder),
            error = painterResource(R.drawable.ic_image_placeholder),
                model = displayUrl,
                contentDescription = "商品图片",
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop
            )
        } else {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(
                    imageVector = Icons.Filled.Image,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.size(36.dp)
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    text = "选择图片",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

@Composable
private fun ErrorBanner(error: String) {
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


@Composable
private fun EditField(label: String, value: String, numeric: Boolean = false, enabled: Boolean = true, onChange: (String) -> Unit) {
    OutlinedTextField(value = value, onValueChange = onChange, label = { Text(label) }, singleLine = true,
        enabled = enabled, modifier = Modifier.fillMaxWidth(),
        keyboardOptions = KeyboardOptions(keyboardType = if (numeric) KeyboardType.Decimal else KeyboardType.Text))
}

private data class MaterialChoice(val id: Int, val skuId: Int?, val label: String)

@Composable
private fun MaterialPicker(label: String, choices: List<MaterialChoice>, id: Int?, skuId: Int?, enabled: Boolean, onSelect: (MaterialChoice) -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    var keyword by remember { mutableStateOf("") }
    val selected = choices.firstOrNull { it.id == id && it.skuId == skuId } ?: choices.firstOrNull { it.id == id }
    Column {
        Text(label, style = MaterialTheme.typography.labelMedium)
        OutlinedButton(onClick = { keyword = ""; expanded = true }, enabled = enabled, modifier = Modifier.fillMaxWidth()) {
            Text(selected?.label ?: "选择材料", modifier = Modifier.fillMaxWidth())
        }
    }
    if (expanded) AlertDialog(
        onDismissRequest = { expanded = false }, title = { Text("选择" + label) },
        text = {
            Column {
                OutlinedTextField(value = keyword, onValueChange = { keyword = it }, label = { Text("搜索材料") }, singleLine = true)
                LazyColumn(modifier = Modifier.height(300.dp)) {
                    val filtered = choices.filter { it.label.contains(keyword.trim(), ignoreCase = true) }
                    if (filtered.isEmpty()) item { Text("暂无匹配材料，请检查搜索或刷新材料") }
                    filtered.forEach { choice -> item(key = "${choice.id}:${choice.skuId}") {
                        TextButton(onClick = { onSelect(choice); expanded = false }, modifier = Modifier.fillMaxWidth()) {
                            Text(choice.label, modifier = Modifier.fillMaxWidth())
                        }
                    } }
                }
            }
        }, confirmButton = { TextButton(onClick = { expanded = false }) { Text("关闭") } }
    )
}
