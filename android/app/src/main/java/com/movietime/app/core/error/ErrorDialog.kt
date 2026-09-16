package com.movietime.app.core.error

import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable


@Composable
fun MovieTimeErrorDialog(
    message: String,
    onDismiss: () -> Unit,
    onRetry: (() -> Unit)? = null
) {

    AlertDialog(

        onDismissRequest = onDismiss,

        title = {
            Text(
                text = "Something went wrong"
            )
        },

        text = {
            Text(
                text = message
            )
        },

        confirmButton = {

            if (onRetry != null) {

                TextButton(
                    onClick = onRetry
                ) {
                    Text(
                        text = "Retry"
                    )
                }

            } else {

                TextButton(
                    onClick = onDismiss
                ) {
                    Text(
                        text = "OK"
                    )
                }
            }
        },

        dismissButton = {

            if (onRetry != null) {

                TextButton(
                    onClick = onDismiss
                ) {
                    Text(
                        text = "Cancel"
                    )
                }
            }
        }
    )
}
