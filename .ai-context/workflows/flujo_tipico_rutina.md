# 1. Iniciar día/sesión
python ai_workflow.py start "optimizar_llamadas_api" --desc "Reducir latencia en llamadas HTTP"

# 2. Analizar problema específico
python ai_workflow.py analyze "llamadas_secuenciales_lentas" \
  --context deep \
  --output current_analysis.md

# 3. Generar prompt para IA
python ai_workflow.py prompt \
  "Convertir llamadas secuenciales a concurrentes" \
  --model deepseek-coder \
  --save

# 4. [Enviar prompt a IA manualmente]

# 5. Procesar respuesta
python ai_workflow.py process response_from_ai.txt \
  --apply-changes \
  --create-tests

# 6. Finalizar sesión
python ai_workflow.py end --success \
  --summary "Implementadas llamadas concurrentes, reducción del 60% en tiempo"
