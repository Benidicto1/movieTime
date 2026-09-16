package com.movietime.app.data.auth

import android.content.Context
import android.util.Base64
import java.nio.charset.StandardCharsets
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

class SecureTokenManager(
    context: Context
) {

    private val applicationContext =
        context.applicationContext

    private val preferences =
        applicationContext.getSharedPreferences(
            PREFS_NAME,
            Context.MODE_PRIVATE
        )

    init {
        createKeyIfNeeded()
    }

    fun saveTokens(
        accessToken: String,
        refreshToken: String
    ) {
        preferences.edit()
            .putString(
                KEY_ACCESS_TOKEN,
                encrypt(accessToken)
            )
            .putString(
                KEY_REFRESH_TOKEN,
                encrypt(refreshToken)
            )
            .apply()
    }

    fun getAccessToken(): String? {

        val encryptedToken =
            preferences.getString(
                KEY_ACCESS_TOKEN,
                null
            )

        return encryptedToken?.let {
            decrypt(it)
        }
    }

    fun getRefreshToken(): String? {

        val encryptedToken =
            preferences.getString(
                KEY_REFRESH_TOKEN,
                null
            )

        return encryptedToken?.let {
            decrypt(it)
        }
    }

    fun clearTokens() {

        preferences.edit()
            .remove(
                KEY_ACCESS_TOKEN
            )
            .remove(
                KEY_REFRESH_TOKEN
            )
            .apply()
    }

    fun isLoggedIn(): Boolean {
        return getAccessToken() != null
    }

    private fun createKeyIfNeeded() {

        val keyStore =
            KeyStore.getInstance(
                ANDROID_KEYSTORE
            ).apply {
                load(null)
            }

        if (
            !keyStore.containsAlias(
                KEY_ALIAS
            )
        ) {

            val keyGenerator =
                KeyGenerator.getInstance(
                    "AES",
                    ANDROID_KEYSTORE
                )

            keyGenerator.init(256)

            keyGenerator.generateKey()
        }
    }

    private fun getSecretKey(): SecretKey {

        val keyStore =
            KeyStore.getInstance(
                ANDROID_KEYSTORE
            ).apply {
                load(null)
            }

        val entry =
            keyStore.getEntry(
                KEY_ALIAS,
                null
            )

        return (
                entry as KeyStore.SecretKeyEntry
                ).secretKey
    }

    private fun encrypt(
        value: String
    ): String {

        val cipher =
            Cipher.getInstance(
                TRANSFORMATION
            )

        cipher.init(
            Cipher.ENCRYPT_MODE,
            getSecretKey()
        )

        val encryptedBytes =
            cipher.doFinal(
                value.toByteArray(
                    StandardCharsets.UTF_8
                )
            )

        val iv =
            cipher.iv

        val combined =
            ByteArray(
                iv.size +
                        encryptedBytes.size
            )

        System.arraycopy(
            iv,
            0,
            combined,
            0,
            iv.size
        )

        System.arraycopy(
            encryptedBytes,
            0,
            combined,
            iv.size,
            encryptedBytes.size
        )

        return Base64.encodeToString(
            combined,
            Base64.NO_WRAP
        )
    }

    private fun decrypt(
        encryptedValue: String
    ): String? {

        return try {

            val combined =
                Base64.decode(
                    encryptedValue,
                    Base64.NO_WRAP
                )

            val iv =
                combined.copyOfRange(
                    0,
                    GCM_IV_LENGTH
                )

            val encryptedBytes =
                combined.copyOfRange(
                    GCM_IV_LENGTH,
                    combined.size
                )

            val cipher =
                Cipher.getInstance(
                    TRANSFORMATION
                )

            val specification =
                GCMParameterSpec(
                    GCM_TAG_LENGTH,
                    iv
                )

            cipher.init(
                Cipher.DECRYPT_MODE,
                getSecretKey(),
                specification
            )

            val decryptedBytes =
                cipher.doFinal(
                    encryptedBytes
                )

            String(
                decryptedBytes,
                StandardCharsets.UTF_8
            )

        } catch (
            exception: Exception
        ) {

            null
        }
    }

    companion object {

        private const val PREFS_NAME =
            "movietime_secure_auth"

        private const val KEY_ACCESS_TOKEN =
            "encrypted_access_token"

        private const val KEY_REFRESH_TOKEN =
            "encrypted_refresh_token"

        private const val KEY_ALIAS =
            "MovieTimeAuthKey"

        private const val ANDROID_KEYSTORE =
            "AndroidKeyStore"

        private const val TRANSFORMATION =
            "AES/GCM/NoPadding"

        private const val GCM_TAG_LENGTH =
            128

        private const val GCM_IV_LENGTH =
            12
    }
}