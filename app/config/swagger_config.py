def custom_openapi(app):
    """
    Customizes the OpenAPI schema to remove schemas globally.
    """
    if app.openapi_schema:  # If the schema is already generated, return it
        return app.openapi_schema

    openapi_schema = app.openapi()  # Generate the default schema

    # Ensure the "components" key exists before modification
    if "components" in openapi_schema:
        openapi_schema["components"].pop("schemas", None)  # Remove the schemas section

    app.openapi_schema = openapi_schema  # Cache the modified schema
    return app.openapi_schema

swagger_config = {
    "title": "Deelflowai API",
    "description": """
        
    """,
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
}
