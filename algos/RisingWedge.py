import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def safe_float(value):
    """Safely convert any value to float."""
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def detect_rising_wedge(df, window_size=5, min_points=3):
    """
    Detects the Rising Wedge pattern in a given DataFrame.
    
    Args:
        df: DataFrame with columns ['High', 'Low', 'Open', 'Close']
        window_size: Rolling window for peak/trough detection
        min_points: Minimum points needed for trendline
    
    Returns:
        tuple: (upper_trendline_indices, lower_trendline_indices, breakdown_index)
    """
    
    # Validate input
    required_cols = ['High', 'Low', 'Open', 'Close']
    if not all(col in df.columns for col in required_cols):
        return [], [], None
    
    if len(df) < window_size * 3:
        return [], [], None
    
    # Convert to simple arrays for processing
    high_values = df['High'].values.astype(float)
    low_values = df['Low'].values.astype(float)
    close_values = df['Close'].values.astype(float)
    indices = list(df.index)
    
    # Remove any NaN values
    valid_mask = ~(np.isnan(high_values) | np.isnan(low_values) | np.isnan(close_values))
    if not np.any(valid_mask):
        return [], [], None
    
    # Find local peaks and troughs using rolling windows
    peaks = []
    troughs = []
    
    half_window = window_size // 2
    
    for i in range(half_window, len(high_values) - half_window):
        if not valid_mask[i]:
            continue
            
        # Check if current point is a local maximum
        is_peak = True
        for j in range(max(0, i - half_window), min(len(high_values), i + half_window + 1)):
            if j != i and valid_mask[j] and high_values[j] > high_values[i]:
                is_peak = False
                break
        
        if is_peak:
            peaks.append((i, indices[i], high_values[i]))
        
        # Check if current point is a local minimum
        is_trough = True
        for j in range(max(0, i - half_window), min(len(low_values), i + half_window + 1)):
            if j != i and valid_mask[j] and low_values[j] < low_values[i]:
                is_trough = False
                break
        
        if is_trough:
            troughs.append((i, indices[i], low_values[i]))
    
    if len(peaks) < min_points or len(troughs) < min_points:
        return [], [], None
    
    # Find best upper trendline (positive slope)
    best_upper_line = None
    best_upper_r2 = -1
    
    for start_idx in range(len(peaks) - min_points + 1):
        for end_idx in range(start_idx + min_points - 1, len(peaks)):
            selected_peaks = peaks[start_idx:end_idx + 1]
            
            if len(selected_peaks) < min_points:
                continue
            
            x_vals = [p[0] for p in selected_peaks]  # position indices
            y_vals = [p[2] for p in selected_peaks]  # high values
            
            if len(x_vals) >= 2:
                try:
                    # Fit line and calculate R-squared
                    coeffs = np.polyfit(x_vals, y_vals, 1)
                    slope, intercept = coeffs[0], coeffs[1]
                    
                    # Check if slope is positive (rising)
                    if slope > 0:
                        # Calculate R-squared
                        y_pred = [slope * x + intercept for x in x_vals]
                        ss_res = sum((y_vals[i] - y_pred[i]) ** 2 for i in range(len(y_vals)))
                        ss_tot = sum((y_vals[i] - np.mean(y_vals)) ** 2 for i in range(len(y_vals)))
                        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                        
                        if r2 > best_upper_r2:
                            best_upper_r2 = r2
                            best_upper_line = {
                                'peaks': selected_peaks,
                                'slope': slope,
                                'intercept': intercept,
                                'r2': r2
                            }
                except:
                    continue
    
    if best_upper_line is None:
        return [], [], None
    
    # Find best lower trendline (positive slope, steeper than upper)
    best_lower_line = None
    best_lower_r2 = -1
    
    for start_idx in range(len(troughs) - min_points + 1):
        for end_idx in range(start_idx + min_points - 1, len(troughs)):
            selected_troughs = troughs[start_idx:end_idx + 1]
            
            if len(selected_troughs) < min_points:
                continue
            
            x_vals = [t[0] for t in selected_troughs]  # position indices
            y_vals = [t[2] for t in selected_troughs]  # low values
            
            if len(x_vals) >= 2:
                try:
                    # Fit line and calculate R-squared
                    coeffs = np.polyfit(x_vals, y_vals, 1)
                    slope, intercept = coeffs[0], coeffs[1]
                    
                    # Check if slope is positive and steeper than upper line
                    if slope > 0 and slope > best_upper_line['slope']:
                        # Calculate R-squared
                        y_pred = [slope * x + intercept for x in x_vals]
                        ss_res = sum((y_vals[i] - y_pred[i]) ** 2 for i in range(len(y_vals)))
                        ss_tot = sum((y_vals[i] - np.mean(y_vals)) ** 2 for i in range(len(y_vals)))
                        r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                        
                        if r2 > best_lower_r2:
                            best_lower_r2 = r2
                            best_lower_line = {
                                'troughs': selected_troughs,
                                'slope': slope,
                                'intercept': intercept,
                                'r2': r2
                            }
                except:
                    continue
    
    if best_lower_line is None:
        return [], [], None
    
    # Extract the indices for return
    upper_trendline = [p[1] for p in best_upper_line['peaks']]  # original indices
    lower_trendline = [t[1] for t in best_lower_line['troughs']]  # original indices
    
    # Look for breakdown point
    breakdown_point = None
    
    # Find the last point of the pattern
    last_upper_pos = max(p[0] for p in best_upper_line['peaks'])
    last_lower_pos = max(t[0] for t in best_lower_line['troughs'])
    last_pattern_pos = max(last_upper_pos, last_lower_pos)
    
    # Check for breakdown after the pattern
    lower_slope = best_lower_line['slope']
    lower_intercept = best_lower_line['intercept']
    
    for i in range(last_pattern_pos + 1, len(close_values)):
        if not valid_mask[i]:
            continue
            
        try:
            projected_lower = lower_slope * i + lower_intercept
            if close_values[i] < projected_lower:
                breakdown_point = indices[i]
                break
        except:
            continue
    
    return upper_trendline, lower_trendline, breakdown_point

def plot_rising_wedge(df, upper_trendline, lower_trendline, breakdown_point, image_path='rising_wedge_pattern.png'):
    """
    Plot the Rising Wedge pattern.
    """
    try:
        plt.figure(figsize=(14, 8))
        
        # Plot price data
        plt.plot(df.index, df['Close'], label='Close Price', linewidth=1.5, color='black', alpha=0.7)
        
        # Plot upper trendline
        if len(upper_trendline) >= 2:
            try:
                # Get values for upper trendline
                upper_x = []
                upper_y = []
                for idx in upper_trendline:
                    if idx in df.index:
                        upper_x.append(idx)
                        upper_y.append(safe_float(df.loc[idx, 'High']))
                
                if len(upper_x) >= 2:
                    # Plot points
                    plt.scatter(upper_x, upper_y, color='red', s=80, label='Upper Peaks', zorder=5, alpha=0.8)
                    
                    # Create extended trendline
                    # Convert indices to positions for fitting
                    pos_x = [list(df.index).index(idx) for idx in upper_x]
                    
                    if len(pos_x) >= 2:
                        slope, intercept = np.polyfit(pos_x, upper_y, 1)
                        
                        # Extend line across chart
                        start_pos = 0
                        end_pos = len(df) - 1
                        line_x_pos = list(range(start_pos, end_pos + 1))
                        line_y = [slope * x + intercept for x in line_x_pos]
                        line_x_idx = [df.index[x] for x in line_x_pos]
                        
                        plt.plot(line_x_idx, line_y, 'r--', linewidth=2, label='Upper Trendline', alpha=0.8)
            except Exception as e:
                print(f"Error plotting upper trendline: {e}")
        
        # Plot lower trendline
        if len(lower_trendline) >= 2:
            try:
                # Get values for lower trendline
                lower_x = []
                lower_y = []
                for idx in lower_trendline:
                    if idx in df.index:
                        lower_x.append(idx)
                        lower_y.append(safe_float(df.loc[idx, 'Low']))
                
                if len(lower_x) >= 2:
                    # Plot points
                    plt.scatter(lower_x, lower_y, color='blue', s=80, label='Lower Troughs', zorder=5, alpha=0.8)
                    
                    # Create extended trendline
                    # Convert indices to positions for fitting
                    pos_x = [list(df.index).index(idx) for idx in lower_x]
                    
                    if len(pos_x) >= 2:
                        slope, intercept = np.polyfit(pos_x, lower_y, 1)
                        
                        # Extend line across chart
                        start_pos = 0
                        end_pos = len(df) - 1
                        line_x_pos = list(range(start_pos, end_pos + 1))
                        line_y = [slope * x + intercept for x in line_x_pos]
                        line_x_idx = [df.index[x] for x in line_x_pos]
                        
                        plt.plot(line_x_idx, line_y, 'b--', linewidth=2, label='Lower Trendline', alpha=0.8)
            except Exception as e:
                print(f"Error plotting lower trendline: {e}")
        
        # Plot breakdown point
        if breakdown_point is not None and breakdown_point in df.index:
            try:
                breakdown_price = safe_float(df.loc[breakdown_point, 'Close'])
                plt.scatter([breakdown_point], [breakdown_price], color='green', s=150, 
                          label='Breakdown Point', zorder=6, marker='v', edgecolors='darkgreen', linewidth=2)
            except Exception as e:
                print(f"Error plotting breakdown point: {e}")
        
        plt.title('Rising Wedge Pattern Detection', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot
        plt.savefig(image_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return image_path
    except Exception as e:
        print(f"Error creating plot: {e}")
        try:
            plt.close()
        except:
            pass
        return None

def invokeRisingWedge(df):
    """
    Main function to detect and analyze Rising Wedge pattern.
    """
    try:
        if len(df) < 20:
            return "Insufficient data for Rising Wedge pattern detection (minimum 20 periods required).", None
        
        # Detect pattern
        upper_trendline, lower_trendline, breakdown_point = detect_rising_wedge(df)
        
        if not upper_trendline or not lower_trendline:
            return "No Rising Wedge pattern detected in the given timeframe.", None
        
        # Generate plot
        image_path = plot_rising_wedge(df, upper_trendline, lower_trendline, breakdown_point)
        
        if not image_path:
            return "Rising Wedge pattern detected but failed to generate visualization.", None
        
        # Create analysis message (no emojis for PDF compatibility)
        message_parts = [
            "RISING WEDGE PATTERN DETECTED",
            "",
            "Pattern Details:",
            f"   - Upper trendline points: {len(upper_trendline)}",
            f"   - Lower trendline points: {len(lower_trendline)}",
            ""
        ]
        
        try:
            current_price = safe_float(df['Close'].iloc[-1])
            message_parts.append(f"Current Price: ${current_price:.2f}")
        except:
            pass
        
        if breakdown_point is not None:
            try:
                breakdown_price = safe_float(df.loc[breakdown_point, 'Close'])
                message_parts.extend([
                    f"Breakdown Price: ${breakdown_price:.2f}",
                    f"Breakdown Date: {breakdown_point}",
                    "",
                    "Status: BREAKDOWN CONFIRMED",
                    "Signal: BEARISH - Pattern has broken down",
                    "Expectation: Further downside movement likely"
                ])
            except:
                message_parts.extend([
                    "",
                    "Status: BREAKDOWN DETECTED",
                    "Signal: BEARISH"
                ])
        else:
            message_parts.extend([
                "",
                "Status: PATTERN FORMING",
                "Watch for potential breakdown below lower trendline",
                "Expected Signal: BEARISH upon breakdown"
            ])
        
        message_parts.extend([
            "",
            "Rising Wedge Characteristics:",
            "   - Both trendlines slope upward",
            "   - Lower trendline steeper than upper",
            "   - Typically bearish reversal pattern",
            "   - Volume often decreases during formation"
        ])
        
        final_message = "\n".join(message_parts)
        return final_message, image_path
        
    except Exception as e:
        return f"Error during Rising Wedge analysis: {str(e)}", None

# Test function for debugging
def test_rising_wedge_with_sample_data():
    """
    Test function with sample data - remove this in production
    """
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # Create rising wedge pattern
    base_trend = np.linspace(100, 120, 100)
    noise = np.random.normal(0, 0.5, 100)
    
    # Upper boundary (slower rise)
    upper_multiplier = 1 + 0.05 * np.sin(np.linspace(0, np.pi, 100)) + 0.02 * np.linspace(0, 1, 100)
    
    # Lower boundary (faster rise)  
    lower_multiplier = 1 - 0.03 * np.sin(np.linspace(0, np.pi, 100)) + 0.04 * np.linspace(0, 1, 100)
    
    high = base_trend * upper_multiplier + noise
    low = base_trend * lower_multiplier + noise
    close = (high + low) / 2 + noise * 0.5
    open_price = close + np.random.normal(0, 0.2, 100)
    
    df = pd.DataFrame({
        'Open': open_price,
        'High': high,
        'Low': low,
        'Close': close
    }, index=dates)
    
    return invokeRisingWedge(df)