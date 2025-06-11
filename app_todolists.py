import streamlit as st
from datetime import date, datetime

# --- CSSでかわいいデザイン ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Comic Neue', cursive;
        background: #FFF0F5;
        color: #5B3756;
    }
    .task-box {
        background: #FDEFF8;
        border-radius: 15px;
        padding: 10px 15px;
        margin-bottom: 10px;
        box-shadow: 2px 3px 8px rgba(155, 89, 182, 0.15);
        transition: background-color 0.3s ease;
    }
    .done-task {
        color: #A8A8A8;
        text-decoration: line-through;
    }
    .overdue {
        color: #FF6B6B;
        font-weight: bold;
    }
    div.stButton > button {
        border-radius: 15px;
        background: #F6B8D3;
        color: #5B3756;
        font-weight: bold;
        padding: 5px 10px;
        border: none;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #E86AA7;
        color: white;
        cursor: pointer;
    }
    label[for^="checkbox_"] {
        cursor: pointer;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("やることリストアプリ")
st.markdown("---")
st.subheader("やることリスト")

if "todo_list" not in st.session_state:
    st.session_state.todo_list = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# タスク追加
st.subheader("新しいタスクを追加")
new_task = st.text_input("タスクを入力してください", placeholder="例: レポートを書く")
priority = st.selectbox("優先度", ["高", "中", "低"], key="priority_input")
due_date = st.date_input("期限を選んでください", value=date.today(), key="due_input")

if st.button("タスクを追加"):
    if new_task:
        st.session_state.todo_list.append({
            "task": new_task,
            "done": False,
            "priority": priority,
            "due": str(due_date)
        })
    else:
        st.error("タスクを入力してください")

priority_order_map = {"高": 0, "中": 1, "低": 2}

st.subheader("📝 やることリスト")

if not st.session_state.todo_list:
    st.info("まだタスクがありません。新しいタスクを追加してみましょう！")
else:
    sorted_list = sorted(
        enumerate(st.session_state.todo_list),
        key=lambda x: (
            datetime.strptime(x[1].get("due", "2100-01-01"), "%Y-%m-%d"),
            priority_order_map.get(x[1].get("priority", "中"), 1)
        )
    )

    total_tasks = len(st.session_state.todo_list)
    completed_tasks = sum(1 for item in st.session_state.todo_list if item["done"])
    st.write(f"**タスク数**: {total_tasks} 件 | **完了**: {completed_tasks} 件 | **残り**: {total_tasks - completed_tasks} 件")

    for i, (original_index, item) in enumerate(sorted_list):
        col1, col2, col3, col4 = st.columns([1, 5, 1, 1])  # 完了 | タスク | 削除 | 編集

        task_due = datetime.strptime(item.get("due", "2100-01-01"), "%Y-%m-%d").date()
        today = date.today()
        is_overdue = not item["done"] and task_due < today

        label_class = "task-box"
        label_text = f"[{item.get('priority', '中')}] {item['task']}（期限: {item.get('due', '未設定')}）"

        if item["done"]:
            label_class += " done-task"
        elif is_overdue:
            label_class += " overdue"

        with col1:
            is_done = st.checkbox("完了", value=item["done"], key=f"checkbox_{original_index}")
            if is_done != item["done"]:
                st.session_state.todo_list[original_index]["done"] = is_done
                st.experimental_rerun()

        with col2:
            st.markdown(f'<div class="{label_class}">{label_text}</div>', unsafe_allow_html=True)

        with col3:
            if st.button("🗑️", key=f"delete_{original_index}"):
                st.session_state.todo_list.pop(original_index)
                st.success("タスクを削除しました")
                st.experimental_rerun()

        with col4:
            if st.button("編集", key=f"edit_{original_index}"):
                st.session_state.edit_index = original_index

# 編集フォームの表示
if st.session_state.edit_index is not None:
    st.markdown("---")
    st.subheader("✏️ タスクを編集")

    edit_index = st.session_state.edit_index
    edit_item = st.session_state.todo_list[edit_index]

    new_text = st.text_input("タスク名", value=edit_item["task"], key="edit_text")
    new_priority = st.selectbox("優先度", ["高", "中", "低"], index=["高", "中", "低"].index(edit_item["priority"]), key="edit_priority")
    new_due = st.date_input("期限", value=datetime.strptime(edit_item["due"], "%Y-%m-%d").date(), key="edit_due")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("保存", key="save_edit"):
            st.session_state.todo_list[edit_index] = {
                "task": new_text,
                "priority": new_priority,
                "due": str(new_due),
                "done": edit_item["done"]
            }
            st.session_state.edit_index = None
            st.success("タスクを更新しました！")
            st.experimental_rerun()

    with col_b:
        if st.button("キャンセル", key="cancel_edit"):
            st.session_state.edit_index = None
            st.info("編集をキャンセルしました")
            st.experimental_rerun()

# 一括操作
if st.session_state.todo_list:
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("全て完了にする"):
            for item in st.session_state.todo_list:
                item["done"] = True
            st.success("全てのタスクを完了にしました！")
            st.experimental_rerun()

    with col2:
        if st.button("完了済みタスクを削除"):
            st.session_state.todo_list = [item for item in st.session_state.todo_list if not item["done"]]
            st.success("完了済みタスクを削除しました")
            st.experimental_rerun()
