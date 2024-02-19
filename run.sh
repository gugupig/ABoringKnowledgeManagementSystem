#!/bin/bash
echo "Starting virtual environment..."
source /root/codebox39/bin/activate

# Start Django
echo "Starting Django..."
cd ~/gpt_projects/ABoringKnowledgeManagementSystem/WebApp
python manage.py runserver 0.0.0.0:8000 &

# Start Streamlit
echo "Starting Streamlit..."
cd ~/gpt_projects/ABoringKnowledgeManagementSystem/Chat
streamlit run run_bot.py streamlit run app.py --client.showSidebarNavigation False &

# Start Flask
echo "Starting Flask..."
cd ~/gpt_projects/ABoringKnowledgeManagementSystem/DocumentIndexing/Embedding
python embedding_service.py &

# Wait for any process to exit
wait

# Kill all background processes on exit
trap "exit" INT TERM ERR
trap "kill 0" EXIT
