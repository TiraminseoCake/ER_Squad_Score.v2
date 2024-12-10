plugins {
    id("com.android.application") version "8.1.1" apply false // Gradle 버전에 맞는 최신 버전 사용
    id("com.google.gms.google-services") version "4.3.15" apply false
    id("com.android.library") version "8.1.1" apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
