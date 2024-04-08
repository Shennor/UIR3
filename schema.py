class RequirementsSchema(object):

    @property
    def requirements_schema(self):
        return {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "general": self.general_schema,
                "images": self.images_schema,
                "tables": self.tables_schema,
                "UDC": {
                    "type": "object",
                    "properties": {
                        "required": {
                            "type": ["boolean", "null"]
                        }
                    },
                    "required": [
                        "required"
                    ]
                },
                "title": self.title_schema,
                "authors": self.authors_schema,
                "affiliation": self.affiliation_schema,
                "annotation": self.annotation_schema,
                "keywords": self.keywords_schema,
                "literature": self.literature_schema,
                "financing": self.required_schema,
                "gratitude": self.required_schema,
                "introduction": self.section_schema,
                "purpose": self.section_schema,
                "materials_methods": self.section_schema,
                "results": self.section_schema,
                "significance": self.section_schema,
                "discussion": self.section_schema,
                "conclusion": self.section_schema,
                "authors_info": self.required_schema,
                "contribution": self.required_schema,
                "documents": self.required_schema
            },
            "required": [
                "general",
                "images",
                "tables",
                "UDC",
                "title",
                "authors",
                "affiliation",
                "annotation",
                "keywords",
                "literature",
                "financing",
                "gratitude",
                "introduction",
                "purpose",
                "materials_methods",
                "results",
                "significance",
                "discussion",
                "conclusion",
                "authors_info",
                "contribution",
                "documents"
            ]
        }

    @property
    def general_schema(self):
        return {
            "type": "object",
            "properties": {
                "font": {
                    "type": ["string", "null"]
                },
                "font_size": {
                    "type": ["integer", "null"]
                },
                "interval": {
                    "type": ["number", "null"]
                },
                "alignment": {
                    "type": ["string", "null"],
                    "enum": ["justify", "left", "right", "center"]
                },
                "columns": {
                    "type": ["boolean", "null"]
                },
                "italic_allowed": {
                    "type": ["boolean", "null"]
                },
                "bold_allowed": {
                    "type": ["boolean", "null"]
                },
                "underlined_allowed": {
                    "type": ["boolean", "null"]
                },
                "double_space_allowed": {
                    "type": ["boolean", "null"]
                },
                "size_min": {
                    "type": ["number", "null"]
                },
                "size_max": {
                    "type": ["number", "null"]
                }
            },
            "required": [
                "font",
                "font_size",
                "interval",
                "alignment",
                "columns",
                "italic_allowed",
                "bold_allowed",
                "underlined_allowed",
                "double_space_allowed",
                "size_min",
                "size_max"
            ]
        }

    @property
    def images_schema(self):
        return {
            "type": "object",
            "properties": {
                "num_min": {
                    "type": ["number", "null"]
                },
                "num_max": {
                    "type": ["number", "null"]
                },
                "width_max": {
                    "type": ["number", "null"]
                },
                "dpi_min": {
                    "type": ["number", "null"]
                },
                "color_allowed": {
                    "type": ["boolean", "null"]
                },
                "links_required": {
                    "type": ["boolean", "null"]
                }
            },
            "required": [
                "num_min",
                "num_max",
                "width_max",
                "dpi_min",
                "color_allowed",
                "links_required"
            ]
        }

    @property
    def tables_schema(self):
        return {
            "type": "object",
            "properties": {
                "font_size": {
                    "type": ["integer", "null"]
                },
                "alignment": {
                    "type": ["string", "null"]
                },
                "width_max": {
                    "type": ["number", "null"]
                },
                "links_required": {
                    "type": ["boolean", "null"]
                }
            },
            "required": [
                "font_size",
                "alignment",
                "width_max",
                "links_required"
            ]
        }

    @property
    def title_schema(self):
        return {
            "type": "object",
            "properties": {
                "font_size": {
                    "type": ["integer", "null"]
                },
                "alignment": {
                    "type": ["string", "null"],
                    "enum": ["justify", "left", "right", "center"]
                },
                "max_length": {
                    "type": ["number", "null"]
                }
            },
            "required": [
                "font_size",
                "alignment",
                "max_length"
            ]
        }

    @property
    def authors_schema(self):
        return {
            "type": "object",
            "properties": {
                "num_max": {
                    "type": ["integer", "null"]
                }
            },
            "required": [
                "num_max"
            ]
        }

    @property
    def affiliation_schema(self):
        return {
            "type": "object",
            "properties": {
                "required": {
                    "type": ["boolean", "null"]
                },
                "info": {
                    "type": ["array", "null"],
                    "items": [
                        {
                            "type": "string"
                        },
                        {
                            "type": "string"
                        },
                        {
                            "type": "boolean"
                        },
                        {
                            "type": "boolean"
                        },
                        {
                            "type": "boolean"
                        },
                        {
                            "type": "boolean"
                        },
                        {
                            "type": "boolean"
                        }
                    ]
                }
            },
            "required": [
                "required",
                "info"
            ]
        }

    @property
    def annotation_schema(self):
        return {
            "type": "object",
            "properties": {
                "required": {
                    "type": ["boolean", "null"]
                },
                "columns": {
                    "type": ["boolean", "null"]
                },
                "size_min": {
                    "type": ["number", "null"]
                },
                "size_max": {
                    "type": ["number", "null"]
                },
                "english": {
                    "type": ["string", "null"]
                }
            },
            "required": [
                "required",
                "columns",
                "size_min",
                "size_max",
                "english"
            ]
        }

    @property
    def keywords_schema(self):
        return {
            "type": "object",
            "properties": {
                "required": {
                    "type": ["boolean", "null"]
                },
                "num_min": {
                    "type": ["integer", "null"]
                },
                "num_max": {
                    "type": ["integer", "null"]
                },
                "english": {
                    "type": ["string", "null"],
                    "enum": ["only", "no", "duplicate"]
                }
            },
            "required": [
                "required",
                "num_min",
                "num_max",
                "english"
            ]
        }

    @property
    def literature_schema(self):
        return {
            "type": "object",
            "properties": {
                "num_min": {
                    "type": ["number", "null"]
                },
                "num_max": {
                    "type": ["number", "null"]
                },
                "style": {
                    "type": ["string", "null"]
                },
                "DOI_required": {
                    "type": ["boolean", "null"]
                },
                "self-citation_part": {
                    "type": ["number", "null"]
                },
                "foreign_part_min": {
                    "type": ["number", "null"]
                },
                "foreign_part_max": {
                    "type": ["number", "null"]
                },
                "novelty_settings": {
                    "type": ["array", "null"],
                    "items": [
                        {
                            "type": "integer"
                        },
                        {
                            "type": "integer"
                        },
                        {
                            "type": "null"
                        }
                    ]
                },
                "antiquity_settings": {
                    "type": ["array", "null"],
                    "items": [
                        {
                            "type": "integer"
                        },
                        {
                            "type": "null"
                        },
                        {
                            "type": "integer"
                        }
                    ]
                }
            },
            "required": [
                "num_min",
                "num_max",
                "style",
                "DOI_required",
                "self-citation_part",
                "foreign_part_min",
                "foreign_part_max",
                "novelty_settings",
                "antiquity_settings"
            ]
        }

    @property
    def section_schema(self):
        return {
            "type": "object",
            "properties": {
                "required": {
                    "type": ["boolean", "null"]
                },
                "size_min": {
                    "type": ["number", "null"]
                },
                "size_max": {
                    "type": ["number", "null"]
                }
            },
            "required": [
                "required",
                "size_min",
                "size_max"
            ]
        }

    @property
    def required_schema(self):
        return {
            "type": "object",
            "properties": {
                "required": {
                    "type": ["boolean", "null"]
                }
            },
            "required": [
                "required"
            ]
        }
