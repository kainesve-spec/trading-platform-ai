# Risk Management

        st.subheader("🎯 Gestion du risque")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Entrée",
                str(signal["entry_price"])
            )

        with col2:
            st.metric(
                "Stop Loss",
                str(signal["stop_loss"])
            )

        with col3:
            st.metric(
                "Take Profit",
                str(signal["take_profit"])
            )

        with col4:
            st.metric(
                "Ratio R/R",
                str(signal["rr_ratio"])
            )


        # Commentaires

        st.subheader("💬 Commentaires")

        comments = signal.get(
            "comments",
            "Aucun commentaire disponible."
        )

        st.write(
            f"• {comments}"
        )

        st.divider()


        # Actions

        if signal["direction"] == "BUY":

            st.success(
                f"✅ Signal ACHAT - Conviction {signal['conviction']:.0f}%"
            )

            if st.button(
                "📥 Ajouter au Portfolio",
                use_container_width=True
            ):

                st.success(
                    "Position ajoutée au portfolio"
                )


        elif signal["direction"] == "SELL":

            st.error(
                f"⛔ Signal VENTE - Conviction {signal['conviction']:.0f}%"
            )

            if st.button(
                "📤 Vendre Position",
                use_container_width=True
            ):

                st.success(
                    "Position vendue"
                )


        else:

            st.warning(
                f"⏸️ Signal neutre - Conviction {signal['conviction']:.0f}%"
            )
