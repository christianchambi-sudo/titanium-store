#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  TITANIUM STORE — Script de arranque
#  Uso: bash start.sh
# ─────────────────────────────────────────────

# Colores
G='\033[0;32m'; Y='\033[1;33m'; R='\033[0;31m'; N='\033[0m'

echo ""
echo -e "${Y}  ████████╗██╗████████╗ █████╗ ███╗  ██╗██╗██╗   ██╗███╗  ███╗${N}"
echo -e "${Y}     ██╔══╝██║╚══██╔══╝██╔══██╗████╗ ██║██║██║   ██║████╗████║${N}"
echo -e "${Y}     ██║   ██║   ██║   ███████║██╔██╗██║██║██║   ██║██╔████╔██║${N}"
echo -e "${Y}     ██║   ██║   ██║   ██╔══██║██║╚████║██║██║   ██║██║╚██╔╝██║${N}"
echo -e "${Y}     ██║   ██║   ██║   ██║  ██║██║ ╚███║██║╚██████╔╝██║ ╚═╝ ██║${N}"
echo -e "${Y}     ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚══╝╚═╝ ╚═════╝ ╚═╝     ╚═╝${N}"
echo ""
echo -e "${G}  TITANIUM STORE — Sistema de catálogo y pedidos v1.0${N}"
echo ""

# Verificar .env
if [ ! -f ".env" ]; then
  echo -e "${Y}⚠️  No se encontró .env — copiando desde .env.example${N}"
  cp .env.example .env
  echo -e "${Y}   Edita .env con tus datos de BD antes de usar en producción.${N}"
fi

# Verificar dependencias
echo -e "${G}📦 Verificando dependencias...${N}"
pip install -r requirements.txt --break-system-packages -q
echo -e "${G}✅ Dependencias OK${N}"
echo ""

# Puertos disponibles
PORT=${PORT:-8000}

echo -e "${G}🚀 Iniciando servidor en http://localhost:${PORT}${N}"
echo ""
echo -e "  📋 Catálogo minorista : ${Y}http://localhost:${PORT}/${N}"
echo -e "  📋 Catálogo mayorista : ${Y}http://localhost:${PORT}/mayor/[token]${N}"
echo -e "  🔐 Panel admin        : ${Y}http://localhost:${PORT}/admin/login${N}"
echo -e "     Usuario admin      : admin / admin123"
echo -e "     Usuario encargado  : encargado / encarg123"
echo ""
echo -e "  ${Y}⚠️  Cambia las contraseñas en app/auth.py antes de usar en producción${N}"
echo ""

uvicorn main:app --host 0.0.0.0 --port $PORT --reload
