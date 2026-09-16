plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}


android {

    namespace = "com.movietime.app"

    compileSdk = 35


    defaultConfig {

        applicationId = "com.movietime.app"

        minSdk = 26

        targetSdk = 35

        versionCode = 1

        versionName = "1.0"

        testInstrumentationRunner =
            "androidx.test.runner.AndroidJUnitRunner"
    }


    buildTypes {

        release {

            isMinifyEnabled = false

            proguardFiles(
                getDefaultProguardFile(
                    "proguard-android-optimize.txt"
                ),
                "proguard-rules.pro"
            )
        }
    }


    compileOptions {

        sourceCompatibility =
            JavaVersion.VERSION_11

        targetCompatibility =
            JavaVersion.VERSION_11
    }


    kotlinOptions {

        jvmTarget = "11"
    }


    buildFeatures {

        compose = true
    }
}


dependencies {

    // ==================================================
    // ANDROID CORE
    // ==================================================

    implementation(
        libs.androidx.core.ktx
    )

    implementation(
        libs.androidx.lifecycle.runtime.ktx
    )

    implementation(
        libs.androidx.activity.compose
    )


    // ==================================================
    // JETPACK COMPOSE
    // ==================================================

    implementation(
        platform(
            libs.androidx.compose.bom
        )
    )

    implementation(
        libs.androidx.compose.ui
    )

    implementation(
        libs.androidx.compose.ui.graphics
    )

    implementation(
        libs.androidx.compose.ui.tooling.preview
    )

    implementation(
        libs.androidx.compose.material3
    )


    // ==================================================
    // NAVIGATION
    // ==================================================

    implementation(
        libs.androidx.navigation.compose
    )


    // ==================================================
    // VIEWMODEL
    // ==================================================

    implementation(
        libs.androidx.lifecycle.viewmodel.compose
    )


    // ==================================================
    // MEDIA / VIDEO PLAYER
    // ==================================================

    implementation(
        libs.androidx.media3.exoplayer
    )

    implementation(
        libs.androidx.media3.ui
    )


    // ==================================================
    // NETWORKING / DJANGO API
    // ==================================================

    implementation(
        "com.squareup.retrofit2:retrofit:2.11.0"
    )

    implementation(
        "com.squareup.retrofit2:converter-gson:2.11.0"
    )

    implementation(
        "com.squareup.okhttp3:okhttp:4.12.0"
    )


    // ==================================================
    // TESTING
    // ==================================================

    testImplementation(
        libs.junit
    )

    androidTestImplementation(
        libs.androidx.junit
    )

    androidTestImplementation(
        libs.androidx.espresso.core
    )

    androidTestImplementation(
        platform(
            libs.androidx.compose.bom
        )
    )

    androidTestImplementation(
        libs.androidx.compose.ui.test.junit4
    )


    // ==================================================
    // DEBUG
    // ==================================================

    debugImplementation(
        libs.androidx.compose.ui.tooling
    )

    debugImplementation(
        libs.androidx.compose.ui.test.manifest
    )
}