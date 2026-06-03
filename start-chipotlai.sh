#!/bin/bash
echo ""
echo "🌯 Starting Chipotlai Max..."
echo "   Powered by Pepper plus retail bot adapter slots"
echo ""

echo "Retail adapter status:"
if [ -n "$HOME_DEPOT_MAGIC_APRON_BASE_URL" ]; then echo "   ✓ Home Depot Magic Apron"; else echo "   · Home Depot Magic Apron: set HOME_DEPOT_MAGIC_APRON_BASE_URL"; fi
if [ -n "$SEPHORA_AI_BEAUTY_CHAT_BASE_URL" ]; then echo "   ✓ Sephora AI Beauty Chat"; else echo "   · Sephora AI Beauty Chat: set SEPHORA_AI_BEAUTY_CHAT_BASE_URL"; fi
if [ -n "$NORDSTROM_ROSIE_BASE_URL" ]; then echo "   ✓ Nordstrom Rosie"; else echo "   · Nordstrom Rosie: set NORDSTROM_ROSIE_BASE_URL"; fi
if [ -n "$LOWES_MYLOW_BASE_URL" ]; then echo "   ✓ Lowe's Mylow"; else echo "   · Lowe's Mylow: set LOWES_MYLOW_BASE_URL"; fi
if [ -n "$IKEA_BILLIE_BASE_URL" ]; then echo "   ✓ IKEA Billie"; else echo "   · IKEA Billie: set IKEA_BILLIE_BASE_URL"; fi
if [ -n "$EXPEDIA_VIRTUAL_AGENT_BASE_URL" ]; then echo "   ✓ Expedia Virtual Agent"; else echo "   · Expedia Virtual Agent: set EXPEDIA_VIRTUAL_AGENT_BASE_URL"; fi
echo ""

# Start the proxy in the background
if [ -d "chipotle-llm-provider" ]; then
  echo "🌶️  Firing up the burrito brain (chipotle-llm-provider)..."
  (cd chipotle-llm-provider && npm install --silent 2>/dev/null && npm run dev) &
  PROXY_PID=$!
  echo "   Proxy PID: $PROXY_PID"
  sleep 2
else
  echo "⚠️  chipotle-llm-provider not found."
  echo "   Run: git submodule update --init"
  echo "   Or start the proxy manually at http://localhost:3000"
fi

echo ""
echo "🧀 Extra guac = longer context window"
echo ""

# Start chipotlai
bun run --cwd packages/opencode --conditions=browser src/index.ts "$@"

# Cleanup proxy on exit
if [ -n "$PROXY_PID" ]; then
  kill $PROXY_PID 2>/dev/null
fi
