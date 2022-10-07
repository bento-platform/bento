/**
 * This file contains typing definitions for Bento-Public JSON config file.
 * You can use it to check your JSON file for its shape by creating a new
 * variable at the bottom of this file.
 * @example
 * const myConfig: bento_public_config = {
 *  ... // type your config here
 * }
 */

type chart_config = {
    /**
     * "Overview" tab layout definition
     * The list of sections defines their order from top to bottom
     */
    overview: {
        /**
         * Title displayed at the top of the section
         */
        section_title: string
        /**
         * List of charts ordered from left to right
         */
        charts: {
            /**
             * field name, must be one of the properties in the `fields` part of the JSON
             */
            field: string,
            /**
             * How the statistics should be displayed
             */
            chart_type: 'bar'|'pie'|CHART_TYPE
        }[]
    }[]
}

type query_config = {
    /**
     * "Search" tab layour definition
     * The list of sections defines their order from top to bottom
     */
    search: {
        /**
         * Title displayed at the top of the section
         */
        section_title: string,
        /**
         * List of field inputs, from top to bottom
         */
        fields: string[]
    }[]
}

type field_config = {
    /**
     * Fields configuration. Order is not important but the name chosen for the
     * field is used in the `overview` and `search` layouts configuration.
     */
    fields: {[k: string]: (field_category | field_date | field_numeric_range)}
}

/**
 * privacy related business rules
 */
type rules_config = {
    rules: {
        /**
         * counts bellow this threshold are not reported back or obfuscated
         */
        count_threshold: number,
        /**
         * Number of fields that can be queried at the same time
         */
        max_query_parameters: number
    }
}

type bento_public_config = field_config & chart_config & query_config & rules_config

type field_base_type = {
    /**
     * model/field identifier used by Katsu for field retrieval
     * Naming must follow the data model
     * @example
     * mapping: 'individual/extra_properties/date_of_consent
     */
    mapping: string
    /**
     * (optional)
     * Similar to `mapping` property. This one must be specified when the field
     * definition relative to the base queryset model used for searching is
     * different from the one used to display statistics.
     * For example, the stats for experiments are not the same as the count
     * of individuals for which a given type of experiment can be found. In the
     * first case, the base model is Experiments, in the later it is Individual.
     * @example
     * mapping_for_query: 'individual/biosamples/experiments/experiment_type
     */
    mapping_for_query?: string
    /**
     * Displayed name for the chart
     * @example
     * title: 'Age'
     */
    title: string
    /**
     * Field description
     */
    description: string
}


/**
 * Properties for numerical binning based on programmatic rules.
 */
type bin_auto_config = {
  bin_size: number,
  taper_left: number,
  taper_right: number,
  minimum: number,
  maximum: number,
}

/**
 * Properties for numerical binning based on given thresholds.
 */
type bin_custom_config = {
  /**
   * List of values defining consecutive bins limits
   * @example
   * "bins": [20, 100, 200, 500]  // creates bins [20-100[, [100-200[, [200-500[
   */
  bins: number[],
  /**
   * (optional)
   * When unset, a first bin is prepended containing all values belows the first
   * bin threshold (e.g. `less than 20`)
   * When set to the same value as the firs bin threshold, no bin is prepended.
   * When set to a value below the first bin threshold, a first bin is prepended
   * with the values from minimum to the first threshold. For example with
   * `bins = [10, 20, 30]` and `minimum = 5`, a bin is prepended with the label
   * `< 10`, counting the values between 5 and 10
   */
  minimum?: number,
  /**
   * (optional)
   * When unset, a last bin is appended with all the values greater than the upper
   * threshold for the defined bins.
   */
  maximum?: number
}

type field_numeric_range = field_base_type & {
    /**
     * Type of field
     */
    datatype: 'number'|DATATYPE.NUMBER,
    /**
     * Field configuration
     */
    config: (bin_auto_config|bin_custom_config) & {
        /**
         * Unit for the numerical value. Can contain UTF8 bitstreams such as `μL`
         */
        units: string
    }
}

type field_date = field_base_type & {
    /**
     * Type of field
     */
    datatype: 'date'|DATATYPE.DATE,
    config: {
        /**
         * method for binning dates.
         * @example
         * bin_by: 'month'
         */
        bin_by: 'month'|DATE_BIN_BY
    }
}

type field_category = field_base_type & {
    /**
     * Type of field
     */
    datatype: 'string'|DATATYPE.STRING,
    config: {
        /** Complete set of the possible values for the field */
        enum: string[]|null  // order matters
    }
}

enum CHART_TYPE {
    BAR = 'bar',
    PIE = 'pie'
}

enum DATATYPE {
    NUMBER = 'number',
    DATE   = 'date',
    STRING = 'string'
}

enum DATE_BIN_BY {
    MONTH = 'month'
}

const config: bento_public_config = {
    overview: [
        {
            section_title: "Demographics",
            charts: [
                {field: 'age', chart_type: CHART_TYPE.BAR},
                {field: 'sex', chart_type: CHART_TYPE.PIE}
            ]
        },
        {
            section_title: "Experiments",
            charts: [
                {field: 'experiment_type', chart_type: CHART_TYPE.PIE},
            ]
        },
    ],
    search: [
        {
            section_title: "Demographics",
            fields: ['age', 'sex']
        }
    ],
    fields: {
        'age': {
            mapping: 'individual/age_numeric',
            title: 'Age',
            description: 'Age at arrival',
            datatype: DATATYPE.NUMBER,
            config: {
                bin_size: 10,
                taper_left: 10,
                taper_right: 100,
                units: 'years',
                minimum: 0,
                maximum: 100
            }
        },
        'sex': {
            mapping: 'individual/sex',
            title: "Sex",
            description: "Sex at birth",
            datatype: DATATYPE.STRING,
            config: {
                enum: null
            }
        },
        'experiment_type': {
            mapping: "experiment/experiment_type",
            title: "Experiment Types",
            description: "Types of experiments performed on a sample",
            datatype: DATATYPE.STRING,
            config: {
                enum: ["DNA Methylation", "mRNA-Seq", "smRNA-Seq", "RNA-Seq", "WES", "Other"]
            }
        },
        "date_of_consent": {
            mapping: "individual/extra_properties/date_of_consent",
            title: "Verbal consent date",
            description: "Date of initial verbal consent(participant, legal representative or tutor), yyyy-mm-dd",
            datatype: DATATYPE.DATE,
            config: {
                bin_by: DATE_BIN_BY.MONTH
            }
        },
        "type_partic": {
            mapping: "individual/extra_properties/type_partic",
            title: "Participant type",
            description: "Has the patient been hospitalized or is the patient seen on as an outpatient?",
            datatype: DATATYPE.STRING,
            config: {
                enum: [
                    "Hospitalized",
                    "Outpatient"
                ]
            }
        },
        "mobility": {
            mapping: "individual/extra_properties/mobility",
            title: "Functional status",
            description: "Mobility",
            datatype: DATATYPE.STRING,
            config: {
                enum: [
                    "I have no problems in walking about",
                    "I have slight problems in walking about",
                    "I have moderate problems in walking about",
                    "I have severe problems in walking about",
                    "I am unable to walk about"
                ]
            }
        }
    },
    "rules": {
        "count_threshold": 5,
        "max_query_parameters": 2
    }
}
