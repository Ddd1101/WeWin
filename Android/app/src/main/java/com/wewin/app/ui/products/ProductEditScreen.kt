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
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Image
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.compose.viewModel
import coil.compose.AsyncImage
import com.wewin.app.data.remote.dto.AccessoryListDto
import com.wewin.app.data.remote.dto.BeadListDto

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
                        onClick = { viewModel.submit() },
                        enabled = !uiState.isSubmitting
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
                    onCodeChange = viewModel::updateCode,
                    onNameChange = viewModel::updateName,
                    onProductTypeChange = viewModel::onProductTypeChange,
                    onPurchaseCostChange = viewModel::updatePurchaseCost,
                    onCostPriceChange = viewModel::updateCostPrice,
                    onSellingPriceChange = viewModel::updateSellingPrice,
                    onLocationChange = viewModel::updateLocation,
                    onSupplierChange = viewModel::updateSupplier,
                    onIsActiveChange = viewModel::updateIsActive,
                    onMaterialChange = viewModel::updateMaterial,
                    onSizeChange = viewModel::updateSize,
                    onColorChange = viewModel::updateColor,
                    onWeightChange = viewModel::updateWeight,
                    onQualityLevelChange = viewModel::updateQualityLevel,
                    onRemarkChange = viewModel::updateRemark,
                    onLaborCostChange = viewModel::updateLaborCost,
                    onElasticCostChange = viewModel::updateElasticCost,
                    onAddBeadComponent = viewModel::addBeadComponent,
                    onRemoveBeadComponent = viewModel::removeBeadComponent,
                    onUpdateBeadComponent = viewModel::updateBeadComponent,
                    onAddAccessoryComponent = viewModel::addAccessoryComponent,
                    onRemoveAccessoryComponent = viewModel::removeAccessoryComponent,
                    onUpdateAccessoryComponent = viewModel::updateAccessoryComponent,
                    onSubmit = viewModel::submit
                )
            }
        }
    }
}

@Composable
private fun ProductEditContent(
    uiState: ProductEditUiState,
    onPickImage: () -> Unit,
    onCodeChange: (String) -> Unit,
    onNameChange: (String) -> Unit,
    onProductTypeChange: (String) -> Unit,
    onPurchaseCostChange: (String) -> Unit,
    onCostPriceChange: (String) -> Unit,
    onSellingPriceChange: (String) -> Unit,
    onLocationChange: (String) -> Unit,
    onSupplierChange: (String) -> Unit,
    onIsActiveChange: (Boolean) -> Unit,
    onMaterialChange: (String) -> Unit,
    onSizeChange: (String) -> Unit,
    onColorChange: (String) -> Unit,
    onWeightChange: (String) -> Unit,
    onQualityLevelChange: (String) -> Unit,
    onRemarkChange: (String) -> Unit,
    onLaborCostChange: (String) -> Unit,
    onElasticCostChange: (String) -> Unit,
    onAddBeadComponent: () -> Unit,
    onRemoveBeadComponent: (Int) -> Unit,
    onUpdateBeadComponent: (Int, Int?, Int?, Int) -> Unit,
    onAddAccessoryComponent: () -> Unit,
    onRemoveAccessoryComponent: (Int) -> Unit,
    onUpdateAccessoryComponent: (Int, Int?, Int?, Int) -> Unit,
    onSubmit: () -> Unit
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { ImagePickerSection(uiState = uiState, onPickImage = onPickImage) }

        if (uiState.error != null) {
            item { ErrorBanner(error = uiState.error) }
        }

        item {
            CommonFieldsCard(
                uiState = uiState,
                onCodeChange = onCodeChange,
                onNameChange = onNameChange,
                onProductTypeChange = onProductTypeChange,
                onPurchaseCostChange = onPurchaseCostChange,
                onCostPriceChange = onCostPriceChange,
                onSellingPriceChange = onSellingPriceChange,
                onLocationChange = onLocationChange,
                onSupplierChange = onSupplierChange,
                onIsActiveChange = onIsActiveChange
            )
        }

        when (uiState.productType) {
            "bead" -> {
                item {
                    BeadFieldsCard(
                        uiState = uiState,
                        onMaterialChange = onMaterialChange,
                        onSizeChange = onSizeChange,
                        onColorChange = onColorChange,
                        onWeightChange = onWeightChange,
                        onQualityLevelChange = onQualityLevelChange,
                        onRemarkChange = onRemarkChange
                    )
                }
            }
            "accessory" -> {
                item {
                    AccessoryFieldsCard(
                        uiState = uiState,
                        onMaterialChange = onMaterialChange,
                        onSizeChange = onSizeChange,
                        onColorChange = onColorChange
                    )
                }
            }
            "finished" -> {
                item {
                    FinishedFieldsCard(
                        uiState = uiState,
                        onLaborCostChange = onLaborCostChange,
                        onElasticCostChange = onElasticCostChange,
                        onAddBeadComponent = onAddBeadComponent,
                        onRemoveBeadComponent = onRemoveBeadComponent,
                        onUpdateBeadComponent = onUpdateBeadComponent,
                        onAddAccessoryComponent = onAddAccessoryComponent,
                        onRemoveAccessoryComponent = onRemoveAccessoryComponent,
                        onUpdateAccessoryComponent = onUpdateAccessoryComponent
                    )
                }
            }
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
    val displayUrl = uiState.initialProduct?.image_url

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(120.dp)
            .clip(shape)
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clickable { onPickImage() },
        contentAlignment = Alignment.Center
    ) {
        if (displayUri != null) {
            AsyncImage(
                model = displayUri,
                contentDescription = "商品图片",
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop
            )
        } else if (!displayUrl.isNullOrBlank()) {
            AsyncImage(
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun CommonFieldsCard(
    uiState: ProductEditUiState,
    onCodeChange: (String) -> Unit,
    onNameChange: (String) -> Unit,
    onProductTypeChange: (String) -> Unit,
    onPurchaseCostChange: (String) -> Unit,
    onCostPriceChange: (String) -> Unit,
    onSellingPriceChange: (String) -> Unit,
    onLocationChange: (String) -> Unit,
    onSupplierChange: (String) -> Unit,
    onIsActiveChange: (Boolean) -> Unit
) {
    FormCard(title = "基本信息") {
        OutlinedTextField(
            value = uiState.code,
            onValueChange = onCodeChange,
            label = { Text("货号 *") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            enabled = !uiState.isEditMode,
            supportingText = {
                if (uiState.isEditMode) {
                    Text("编辑模式下货号不可修改")
                }
            }
        )

        OutlinedTextField(
            value = uiState.name,
            onValueChange = onNameChange,
            label = { Text("商品名称 *") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        Text(
            text = "商品类型",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        if (uiState.isEditMode) {
            OutlinedTextField(
                value = productTypeDisplay(uiState.productType),
                onValueChange = {},
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                enabled = false,
                readOnly = true
            )
        } else {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                val types = listOf(
                    "bead" to "串珠",
                    "accessory" to "配件",
                    "finished" to "成品"
                )
                types.forEach { (type, label) ->
                    FilterChip(
                        selected = uiState.productType == type,
                        onClick = { onProductTypeChange(type) },
                        label = { Text(label) }
                    )
                }
            }
        }

        OutlinedTextField(
            value = uiState.purchaseCost,
            onValueChange = onPurchaseCostChange,
            label = { Text("采购成本") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )

        OutlinedTextField(
            value = uiState.costPrice,
            onValueChange = onCostPriceChange,
            label = { Text("单颗成本") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            supportingText = {
                if (uiState.productType == "bead") {
                    Text("串珠成本后端自动计算（采购成本×克重）")
                }
            }
        )

        OutlinedTextField(
            value = uiState.sellingPrice,
            onValueChange = onSellingPriceChange,
            label = { Text("售价") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )

        OutlinedTextField(
            value = uiState.location,
            onValueChange = onLocationChange,
            label = { Text("库位") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        OutlinedTextField(
            value = uiState.supplier,
            onValueChange = onSupplierChange,
            label = { Text("供应商") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = "启用",
                style = MaterialTheme.typography.bodyLarge
            )
            Switch(
                checked = uiState.isActive,
                onCheckedChange = onIsActiveChange
            )
        }
    }
}

@Composable
private fun BeadFieldsCard(
    uiState: ProductEditUiState,
    onMaterialChange: (String) -> Unit,
    onSizeChange: (String) -> Unit,
    onColorChange: (String) -> Unit,
    onWeightChange: (String) -> Unit,
    onQualityLevelChange: (String) -> Unit,
    onRemarkChange: (String) -> Unit
) {
    FormCard(title = "串珠参数") {
        OutlinedTextField(
            value = uiState.material,
            onValueChange = onMaterialChange,
            label = { Text("材质") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        OutlinedTextField(
            value = uiState.size,
            onValueChange = onSizeChange,
            label = { Text("规格(mm)") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )
        OutlinedTextField(
            value = uiState.color,
            onValueChange = onColorChange,
            label = { Text("颜色") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        OutlinedTextField(
            value = uiState.weight,
            onValueChange = onWeightChange,
            label = { Text("克重(g)") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )
        OutlinedTextField(
            value = uiState.qualityLevel,
            onValueChange = onQualityLevelChange,
            label = { Text("品质等级(1-10)") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )
        OutlinedTextField(
            value = uiState.remark,
            onValueChange = onRemarkChange,
            label = { Text("备注") },
            modifier = Modifier.fillMaxWidth(),
            minLines = 2
        )
    }
}

@Composable
private fun AccessoryFieldsCard(
    uiState: ProductEditUiState,
    onMaterialChange: (String) -> Unit,
    onSizeChange: (String) -> Unit,
    onColorChange: (String) -> Unit
) {
    FormCard(title = "配件参数") {
        OutlinedTextField(
            value = uiState.material,
            onValueChange = onMaterialChange,
            label = { Text("材质") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        OutlinedTextField(
            value = uiState.size,
            onValueChange = onSizeChange,
            label = { Text("规格(mm)") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
        )
        OutlinedTextField(
            value = uiState.color,
            onValueChange = onColorChange,
            label = { Text("颜色") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
    }
}

@Composable
private fun FinishedFieldsCard(
    uiState: ProductEditUiState,
    onLaborCostChange: (String) -> Unit,
    onElasticCostChange: (String) -> Unit,
    onAddBeadComponent: () -> Unit,
    onRemoveBeadComponent: (Int) -> Unit,
    onUpdateBeadComponent: (Int, Int?, Int?, Int) -> Unit,
    onAddAccessoryComponent: () -> Unit,
    onRemoveAccessoryComponent: (Int) -> Unit,
    onUpdateAccessoryComponent: (Int, Int?, Int?, Int) -> Unit
) {
    FormCard(title = "成品参数") {
        OutlinedTextField(
            value = uiState.laborCost,
            onValueChange = onLaborCostChange,
            label = { Text("工费") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )
        OutlinedTextField(
            value = uiState.elasticCost,
            onValueChange = onElasticCostChange,
            label = { Text("弹性成本") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal)
        )

        Spacer(Modifier.height(8.dp))
        Text(
            text = "串珠组成",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold
        )
        uiState.beadComponents.forEachIndexed { index, component ->
            BeadComponentRow(
                index = index,
                component = component,
                beadOptions = uiState.beadOptions,
                onRemove = { onRemoveBeadComponent(index) },
                onUpdate = { beadId, skuId, quantity ->
                    onUpdateBeadComponent(index, beadId, skuId, quantity)
                }
            )
        }
        Button(
            onClick = onAddBeadComponent,
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Filled.Add, contentDescription = null)
            Spacer(Modifier.width(4.dp))
            Text("添加串珠")
        }

        Spacer(Modifier.height(8.dp))
        Text(
            text = "配件组成",
            style = MaterialTheme.typography.titleSmall,
            fontWeight = FontWeight.Bold
        )
        uiState.accessoryComponents.forEachIndexed { index, component ->
            AccessoryComponentRow(
                index = index,
                component = component,
                accessoryOptions = uiState.accessoryOptions,
                onRemove = { onRemoveAccessoryComponent(index) },
                onUpdate = { accessoryId, skuId, quantity ->
                    onUpdateAccessoryComponent(index, accessoryId, skuId, quantity)
                }
            )
        }
        Button(
            onClick = onAddAccessoryComponent,
            modifier = Modifier.fillMaxWidth()
        ) {
            Icon(Icons.Filled.Add, contentDescription = null)
            Spacer(Modifier.width(4.dp))
            Text("添加配件")
        }
    }
}

@Composable
private fun BeadComponentRow(
    index: Int,
    component: BeadComponent,
    beadOptions: List<BeadListDto.BeadListItem>,
    onRemove: () -> Unit,
    onUpdate: (Int?, Int?, Int) -> Unit
) {
    var beadMenuExpanded by rememberSaveable { mutableStateOf(false) }
    var skuMenuExpanded by rememberSaveable { mutableStateOf(false) }
    var quantityText by rememberSaveable(index, component.beadId) {
        mutableStateOf(component.quantity.toString())
    }

    val selectedBead = beadOptions.find { it.id == component.beadId }
    val selectedSku = selectedBead?.skus?.find { it.id == component.skuId }

    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
        shape = RoundedCornerShape(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "串珠 #${index + 1}",
                    style = MaterialTheme.typography.labelMedium,
                    modifier = Modifier.weight(1f)
                )
                IconButton(onClick = onRemove) {
                    Icon(
                        imageVector = Icons.Filled.Delete,
                        contentDescription = "删除",
                        tint = MaterialTheme.colorScheme.error
                    )
                }
            }

            // 串珠选择
            Box(modifier = Modifier.fillMaxWidth()) {
                OutlinedTextField(
                    value = selectedBead?.let { "${it.code} - ${it.name}" } ?: "请选择串珠",
                    onValueChange = {},
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { beadMenuExpanded = true },
                    readOnly = true,
                    trailingIcon = {
                        Icon(Icons.Filled.ArrowDropDown, contentDescription = null)
                    }
                )
                DropdownMenu(
                    expanded = beadMenuExpanded,
                    onDismissRequest = { beadMenuExpanded = false }
                ) {
                    beadOptions.forEach { bead ->
                        DropdownMenuItem(
                            text = { Text("${bead.code} - ${bead.name}") },
                            onClick = {
                                onUpdate(bead.id, null, component.quantity)
                                beadMenuExpanded = false
                            }
                        )
                    }
                }
            }

            // SKU 选择（可选）
            if (selectedBead != null && selectedBead.skus.isNotEmpty()) {
                Box(modifier = Modifier.fillMaxWidth()) {
                    OutlinedTextField(
                        value = selectedSku?.let {
                            it.sku_code ?: it.sku_name ?: "SKU#${it.id}"
                        } ?: "选择 SKU（可选）",
                        onValueChange = {},
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { skuMenuExpanded = true },
                        readOnly = true,
                        enabled = false,
                        trailingIcon = {
                            Icon(Icons.Filled.ArrowDropDown, contentDescription = null)
                        }
                    )
                    DropdownMenu(
                        expanded = skuMenuExpanded,
                        onDismissRequest = { skuMenuExpanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("不指定 SKU") },
                            onClick = {
                                onUpdate(component.beadId, null, component.quantity)
                                skuMenuExpanded = false
                            }
                        )
                        selectedBead.skus.forEach { sku ->
                            DropdownMenuItem(
                                text = {
                                    Text(sku.sku_code ?: sku.sku_name ?: "SKU#${sku.id}")
                                },
                                onClick = {
                                    onUpdate(component.beadId, sku.id, component.quantity)
                                    skuMenuExpanded = false
                                }
                            )
                        }
                    }
                }
            }

            // 数量
            OutlinedTextField(
                value = quantityText,
                onValueChange = { value ->
                    quantityText = value.filter { it.isDigit() }
                    val qty = quantityText.toIntOrNull() ?: 0
                    onUpdate(component.beadId, component.skuId, qty)
                },
                label = { Text("数量") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
        }
    }
}

@Composable
private fun AccessoryComponentRow(
    index: Int,
    component: AccessoryComponent,
    accessoryOptions: List<AccessoryListDto.AccessoryListItem>,
    onRemove: () -> Unit,
    onUpdate: (Int?, Int?, Int) -> Unit
) {
    var accessoryMenuExpanded by rememberSaveable { mutableStateOf(false) }
    var skuMenuExpanded by rememberSaveable { mutableStateOf(false) }
    var quantityText by rememberSaveable(index, component.accessoryId) {
        mutableStateOf(component.quantity.toString())
    }

    val selectedAccessory = accessoryOptions.find { it.id == component.accessoryId }
    val selectedSku = selectedAccessory?.skus?.find { it.id == component.skuId }

    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
        shape = RoundedCornerShape(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(8.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "配件 #${index + 1}",
                    style = MaterialTheme.typography.labelMedium,
                    modifier = Modifier.weight(1f)
                )
                IconButton(onClick = onRemove) {
                    Icon(
                        imageVector = Icons.Filled.Delete,
                        contentDescription = "删除",
                        tint = MaterialTheme.colorScheme.error
                    )
                }
            }

            // 配件选择
            Box(modifier = Modifier.fillMaxWidth()) {
                OutlinedTextField(
                    value = selectedAccessory?.let { "${it.code} - ${it.name}" }
                        ?: "请选择配件",
                    onValueChange = {},
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { accessoryMenuExpanded = true },
                    readOnly = true,
                    trailingIcon = {
                        Icon(Icons.Filled.ArrowDropDown, contentDescription = null)
                    }
                )
                DropdownMenu(
                    expanded = accessoryMenuExpanded,
                    onDismissRequest = { accessoryMenuExpanded = false }
                ) {
                    accessoryOptions.forEach { accessory ->
                        DropdownMenuItem(
                            text = { Text("${accessory.code} - ${accessory.name}") },
                            onClick = {
                                onUpdate(accessory.id, null, component.quantity)
                                accessoryMenuExpanded = false
                            }
                        )
                    }
                }
            }

            // SKU 选择（可选）
            if (selectedAccessory != null && selectedAccessory.skus.isNotEmpty()) {
                Box(modifier = Modifier.fillMaxWidth()) {
                    OutlinedTextField(
                        value = selectedSku?.let {
                            it.sku_code ?: it.sku_name ?: "SKU#${it.id}"
                        } ?: "选择 SKU（可选）",
                        onValueChange = {},
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable { skuMenuExpanded = true },
                        readOnly = true,
                        enabled = false,
                        trailingIcon = {
                            Icon(Icons.Filled.ArrowDropDown, contentDescription = null)
                        }
                    )
                    DropdownMenu(
                        expanded = skuMenuExpanded,
                        onDismissRequest = { skuMenuExpanded = false }
                    ) {
                        DropdownMenuItem(
                            text = { Text("不指定 SKU") },
                            onClick = {
                                onUpdate(component.accessoryId, null, component.quantity)
                                skuMenuExpanded = false
                            }
                        )
                        selectedAccessory.skus.forEach { sku ->
                            DropdownMenuItem(
                                text = {
                                    Text(sku.sku_code ?: sku.sku_name ?: "SKU#${sku.id}")
                                },
                                onClick = {
                                    onUpdate(component.accessoryId, sku.id, component.quantity)
                                    skuMenuExpanded = false
                                }
                            )
                        }
                    }
                }
            }

            // 数量
            OutlinedTextField(
                value = quantityText,
                onValueChange = { value ->
                    quantityText = value.filter { it.isDigit() }
                    val qty = quantityText.toIntOrNull() ?: 0
                    onUpdate(component.accessoryId, component.skuId, qty)
                },
                label = { Text("数量") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number)
            )
        }
    }
}

@Composable
private fun FormCard(
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

private fun productTypeDisplay(type: String): String {
    return when (type) {
        "bead" -> "串珠"
        "accessory" -> "配件"
        "finished" -> "成品"
        else -> type
    }
}
