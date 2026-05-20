# Makefile for WeWin 项目

.PHONY: help install-backend install-frontend run-backend run-frontend build-frontend format-backend format-frontend lint-backend lint-frontend

help:
	@echo "可用的命令："
	@echo "  install-backend  - 安装后端依赖"
	@echo "  install-frontend - 安装前端依赖"
	@echo "  run-backend      - 运行后端服务"
	@echo "  run-frontend     - 运行前端开发服务器"
	@echo "  build-frontend   - 构建前端生产版本"
	@echo "  format-backend   - 格式化后端代码"
	@echo "  format-frontend  - 格式化前端代码"
	@echo "  lint-backend     - 检查后端代码"
	@echo "  lint-frontend    - 检查前端代码"

install-backend:
	cd Server && pip install -r requirements.txt

install-frontend:
	cd Page && npm install

run-backend:
	cd Server && source venv/bin/activate && python manage.py