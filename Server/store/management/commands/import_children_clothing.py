import os

import openpyxl
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from company.models import Company
from store.models import Product, ProductType, ProductSku, ChildrenClothing


class Command(BaseCommand):
    help = '从 price.xlsx 导入童装商品（货号→商品，尺码→SKU）'

    def add_arguments(self, parser):
        parser.add_argument('--xlsx', default=None, help='xlsx 文件路径（默认 AliData/price.xlsx）')
        parser.add_argument('--company-id', type=int, default=1, help='企业 ID（默认 1）')

    def handle(self, *args, **options):
        xlsx_path = options['xlsx'] or os.path.join(
            settings.BASE_DIR, '..', 'AliData', 'price.xlsx'
        )
        company = Company.objects.get(id=options['company_id'])

        wb = openpyxl.load_workbook(xlsx_path, data_only=True)
        ws = wb[wb.sheetnames[0]]

        # 表头：第 8 列起是尺码
        headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]

        created = 0
        skipped = 0
        sku_count = 0

        for r in range(2, ws.max_row + 1):
            raw_code = ws.cell(r, 1).value
            if raw_code is None:
                continue
            code = str(raw_code).strip()

            # 已存在则跳过
            if Product.objects.filter(code=code, company=company).exists():
                skipped += 1
                continue

            raw_name = ws.cell(r, 2).value
            name = str(raw_name).strip() if raw_name else code
            supplier = str(ws.cell(r, 3).value or '').strip()

            # 收集尺码成本（第 8 列起）
            size_costs = []
            for c in range(8, ws.max_column + 1):
                size = headers[c - 1]
                cost = ws.cell(r, c).value
                if size is None or cost is None:
                    continue
                size_costs.append((size, float(cost)))

            if not size_costs:
                skipped += 1
                continue

            min_cost = min(cost for _, cost in size_costs)
            sizes = [str(s) for s, _ in size_costs]
            size_desc = f'{sizes[0]}-{sizes[-1]}' if len(sizes) > 1 else sizes[0]

            with transaction.atomic():
                product = Product.objects.create(
                    code=code,
                    name=name,
                    product_type=ProductType.CHILDREN_CLOTHING,
                    purchase_cost=min_cost,
                    cost_price=min_cost,
                    selling_price=0,
                    supplier=supplier,
                    company=company,
                    is_active=True,
                )
                ChildrenClothing.objects.create(
                    product=product,
                    fabric=name,
                    size=size_desc,
                    color='',
                    season='',
                    gender='',
                    age_range='',
                )
                for i, (size, cost) in enumerate(size_costs):
                    if isinstance(size, (int, float)):
                        sku_size = int(size)
                        sku_name = str(int(size))
                    else:
                        sku_size = None
                        sku_name = str(size)
                    ProductSku.objects.create(
                        product=product,
                        sku_code=f'{code}-{size}',
                        name=sku_name,
                        size=sku_size,
                        cost_price=cost,
                        selling_price=0,
                        is_default=(i == 0),
                        is_active=True,
                    )
                    sku_count += 1

            created += 1

        self.stdout.write(self.style.SUCCESS(
            f'导入完成：新增 {created} 个商品，{sku_count} 个 SKU，跳过 {skipped} 个'
        ))
