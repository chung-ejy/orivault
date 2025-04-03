class RollingFactorAnalysis:
    
    @staticmethod
    def apply(df, y_variable, x_variable, window):
        """
        Apply rolling factor loadings to a DataFrame.

        Parameters:
        - df (DataFrame): The input DataFrame.
        - y_variable (str): The dependent variable.
        - x_variable (str): The independent variable.
        - window (int): The rolling window size for calculations.

        Returns:
        - DataFrame: The updated DataFrame with calculated columns.
        """
        # Validate inputs
        if y_variable not in df.columns or x_variable not in df.columns:
            raise KeyError(f"Columns '{y_variable}' and/or '{x_variable}' not found in the DataFrame.")
        
        # Calculate rolling covariance and variance
        df["cov"] = df[y_variable].rolling(window).cov(df[x_variable])
        df["var"] = df[x_variable].rolling(window).var()
        
        # Calculate beta
        df["beta"] = df["cov"] / df["var"]
        
        # Predict values for y_variable based on beta and x_variable
        df[f"{y_variable}_prediction"] = df["beta"] * df[x_variable]
        
        return df