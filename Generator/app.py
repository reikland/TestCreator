import streamlit as st

from csv_export import build_csv
from editor import edit_topics_with_llm
from judge import rank_topics
from llm import build_openrouter_client, normalize_openai_model_name
from state import init_session_state, safe_rerun
from topic_generation import generate_topics
from app_types import AppRunConfig


def render_sidebar() -> AppRunConfig:
    st.sidebar.header("OpenRouter")

    api_key = st.sidebar.text_input(
        "OpenRouter API key",
        type="password",
        help="sk-or-...",
    )

    st.sidebar.header("Models")
    gen_model = st.sidebar.text_input("Generation model", value="perplexity/sonar")
    judge_model = st.sidebar.text_input(
        "Judge / ranking model",
        value="anthropic/claude-3.5-sonnet",
    )

    st.sidebar.header("Generation parameters")
    target_n = st.sidebar.slider("Number of topics (X)", 10, 300, 100, step=10)
    top_k = st.sidebar.slider("Top-K final questions", 5, 20, 10)
    batch_n = st.sidebar.slider("Batch size", 10, 80, 40)
    max_rounds = st.sidebar.slider("Max rounds", 1, 20, 10)

    additional_instructions = st.sidebar.text_area(
        "Additional instructions",
        value=(
            "Return concise, forecasting-relevant topics. "
            "Each topic should be concrete, time-bounded, and suitable for a probabilistic forecasting question. "
            "Avoid duplicates and near-duplicates."
        ),
    )

    return AppRunConfig(
        openrouter_api_key=api_key,
        gen_model=gen_model,
        judge_model=judge_model,
        target_n=target_n,
        top_k=top_k,
        batch_n=batch_n,
        max_rounds=max_rounds,
        additional_instructions=additional_instructions,
    )


def main() -> None:
    st.set_page_config(page_title="Forecasting Topic Generator", layout="wide")
    init_session_state()

    st.title("Forecasting Topic Generator")

    cfg = render_sidebar()

    if not cfg.openrouter_api_key:
        st.info("Enter your OpenRouter API key to continue.")
        st.stop()

    client = build_openrouter_client(cfg.openrouter_api_key)

    col1, col2 = st.columns([1, 1])
    with col1:
        run_clicked = st.button("Generate topics (new run)")

    with col2:
        if st.button("Clear results"):
            st.session_state.topics = None
            st.session_state.top_topics = None
            st.session_state.csv_data = None
            st.session_state.edited_csv_data = None
            st.session_state.is_csv_edited = False
            st.session_state.csv_version += 1
            safe_rerun()

    # -------------------------
    # RUN PIPELINE
    # -------------------------
    if run_clicked:
        with st.spinner("Generating topics..."):
            topics = generate_topics(
                gen_model=cfg.gen_model,
                target_n=cfg.target_n,
                batch_n=cfg.batch_n,
                max_rounds=cfg.max_rounds,
                additional_instructions=cfg.additional_instructions,
            )

        with st.spinner("Selecting best questions with LLM..."):
            top_topics = rank_topics(
                client=client,
                judge_model=normalize_openai_model_name(cfg.judge_model),
                topics=topics,
                top_k=cfg.top_k,
            )

        st.session_state.topics = topics
        st.session_state.top_topics = top_topics
        st.session_state.csv_data = build_csv(top_topics)
        st.session_state.edited_csv_data = None
        st.session_state.is_csv_edited = False
        st.session_state.csv_version += 1

    # -------------------------
    # DISPLAY + EDIT
    # -------------------------
    if st.session_state.top_topics is not None:
        st.subheader("Top forecasting questions")
        st.table(st.session_state.top_topics)

        st.markdown("---")
        st.subheader("Modify topics with LLM")

        edit_prompt = st.text_area(
            "Describe how to adjust the ranked topics",
            placeholder=(
                "e.g., focus on AI governance, keep time horizons under five years, "
                "and avoid overlapping questions"
            ),
        )

        edit_clicked = st.button("Apply edit prompt with judge model")

        if edit_clicked:
            if not edit_prompt.strip():
                st.warning("Add instructions for how the topics should be edited.")
            else:
                try:
                    with st.spinner("Updating topics with the judge model..."):
                        updated_topics = edit_topics_with_llm(
                            client=client,
                            model_name=normalize_openai_model_name(cfg.judge_model),
                            topics=st.session_state.top_topics,
                            user_prompt=edit_prompt,
                        )
                except ValueError as error:
                    st.error(str(error))
                else:
                    st.session_state.top_topics = updated_topics
                    st.session_state.csv_data = build_csv(updated_topics)
                    st.session_state.edited_csv_data = st.session_state.csv_data
                    st.session_state.is_csv_edited = True
                    st.session_state.csv_version += 1
                    safe_rerun()

        # -------------------------
        # CSV EXPORT
        # -------------------------
        csv_data = st.session_state.csv_data
        if csv_data:
            is_edited = st.session_state.is_csv_edited
            st.markdown("---")
            st.subheader("Export")

            st.download_button(
                label="Download edited CSV" if is_edited else "Download CSV",
                data=csv_data,
                file_name="top_forecasting_questions_edited.csv"
                if is_edited
                else "top_forecasting_questions.csv",
                mime="text/csv",
                key=f"csv_download_v{st.session_state.csv_version}",
            )


if __name__ == "__main__":
    main()
