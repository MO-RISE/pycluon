
cmake_minimum_required(VERSION 3.14 FATAL_ERROR)

# Project
project(pycluon LANGUAGES CXX)

# Fetch CPM
set(CPM_DOWNLOAD_VERSION 0.32.0) 
set(CPM_DOWNLOAD_LOCATION "${CMAKE_CURRENT_BINARY_DIR}/cmake/CPM_${CPM_DOWNLOAD_VERSION}.cmake")
if(NOT (EXISTS ${CPM_DOWNLOAD_LOCATION}))
  message(STATUS "Downloading CPM.cmake v${CPM_DOWNLOAD_VERSION}")
  file(DOWNLOAD https://github.com/cpm-cmake/CPM.cmake/releases/download/v${CPM_DOWNLOAD_VERSION}/CPM.cmake ${CPM_DOWNLOAD_LOCATION})
endif()
include(${CPM_DOWNLOAD_LOCATION})

# Add dependencies
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)


CPMAddPackage(
  NAME cluon
  GITHUB_REPOSITORY chrberger/libcluon
  VERSION 0.0.140
  SOURCE_SUBDIR libcluon
  EXCLUDE_FROM_ALL YES
  GIT_SHALLOW YES
  PATCH_COMMAND git apply ${CMAKE_SOURCE_DIR}/external/libcluon_CMakeLists_disable_tests.patch
)

CPMAddPackage(
  NAME pybind11
  GITHUB_REPOSITORY pybind/pybind11
  GIT_TAG v2.6.1
)


# Create executable
pybind11_add_module(${PROJECT_NAME} src/pycluon.cpp)
target_include_directories(${PROJECT_NAME} 
  PRIVATE 
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  # cluon specific inludes
  ${cluon_SOURCE_DIR}/libcluon/include
  ${cluon_SOURCE_DIR}/libcluon/thirdparty
  ${cluon_SOURCE_DIR}/libcluon/tools
  ${CMAKE_CURRENT_BINARY_DIR}/include # libcluon "built-in" message specifications

)
target_link_libraries(${PROJECT_NAME} PRIVATE Threads::Threads cluon-static -static-libgcc -static-libstdc++)
if(UNIX)
  target_link_libraries(${PROJECT_NAME} PRIVATE rt)
endif()
set_target_properties(${PROJECT_NAME} PROPERTIES OUTPUT_NAME _pycluon)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED true)

add_dependencies(${PROJECT_NAME} cluon-msc)
add_dependencies(${PROJECT_NAME} cluon-OD4toStdout)
add_dependencies(${PROJECT_NAME} cluon-OD4toJSON)
add_dependencies(${PROJECT_NAME} cluon-LCMtoJSON)
add_dependencies(${PROJECT_NAME} cluon-filter)
add_dependencies(${PROJECT_NAME} cluon-livefeed)
add_dependencies(${PROJECT_NAME} cluon-rec2csv)
add_dependencies(${PROJECT_NAME} cluon-replay)

install(TARGETS ${PROJECT_NAME} DESTINATION pycluon)

install(TARGETS cluon-msc DESTINATION pycluon/bin)
install(TARGETS cluon-OD4toStdout DESTINATION pycluon/bin)
install(TARGETS cluon-OD4toJSON DESTINATION pycluon/bin)
install(TARGETS cluon-LCMtoJSON DESTINATION pycluon/bin)
install(TARGETS cluon-filter DESTINATION pycluon/bin)
install(TARGETS cluon-livefeed DESTINATION pycluon/bin)
install(TARGETS cluon-rec2csv DESTINATION pycluon/bin)
install(TARGETS cluon-replay DESTINATION pycluon/bin)

install(
  FILES ${cluon_SOURCE_DIR}/libcluon/resources/cluonDataStructures.odvd
  RENAME cluon_data_structures.odvd
  DESTINATION pycluon/resources)

