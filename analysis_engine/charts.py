"""
Charting functions with matplotlib, numpy, pandas, and seaborn

Change the footnote with:

::

    export PLOT_FOOTNOTE="custom footnote on images"

.. note: these functions were ported from
         the repo: https://github.com/jay-johnson/scipype

"""

import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import analysis_engine.build_result as build_result
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import ERR
from analysis_engine.consts import PLOT_COLORS
from analysis_engine.consts import ev
from analysis_engine.consts import get_status

log = build_colorized_logger(
    name=__name__)


def add_footnote(
        fig=None,
        xpos=0.90,
        ypos=0.01):
    """pd_add_footnote

    Add a footnote based off the environment key:
    ``PLOT_FOOTNOTE``

    :param fig: add the footnote to this figure object
    """
    if not fig:
        return

    footnote_text = ev(
        'PLOT_FOOTNOTE',
        'algotraders')
    fig.text(
        0.90,
        0.01,
        footnote_text,
        va='bottom',
        fontsize=8,
        color='#888888')
# end of add_footnote


def set_common_seaborn_fonts():
    """set_common_seaborn_fonts

    Set the font and text style
    """
    sns.set(font='serif')
    sns.set_context(
        'paper',
        rc={
            'font.size': 12,
            'axes.titlesize': 12,
            'axes.labelsize': 10
        }
    )
# end of set_common_seaborn_fonts


def send_final_log(
        log_label,
        fn_name,
        result):
    """send_final_log

    :param log_label: log identifier
    :param fn_name: function name
    :param result: dictionary result
    """

    if not fn_name:
        log.error(
            '{} missing fn_name parameter for send_final_log'.format(
                log_label))
        return

    if not result:
        log.error(
            '{} missing result parameter for send_final_log'.format(
                log_label))
        return

    str_result = (
        '{} - {} - done status={} '
        'err={}'.format(
            log_label,
            fn_name,
            get_status(result['status']),
            result['err']))

    if result['status'] == ERR:
        log.error(str_result)
    else:
        log.info(str_result)
    # handle log based off status

# end of send_final_log


def show_with_entities(
        log_label,
        xlabel,
        ylabel,
        title,
        ax,
        fig,
        legend_list=None,
        show_plot=True):
    """show_with_entities

    Helper for showing a plot with a legend and a
    footnoe

    :param log_label: log identifier
    :param xlabel: x-axis label
    :param ylabel: y-axis label
    :param title: title of the plot
    :param ax: axes
    :param fig: figure
    :param legend_list: list of legend items to show
    :param show_plot: bool to show the plot
    """

    log.debug(
        '{} - '
        'show_with_entities'
        ' - start'.format(
            log_label))

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    ax.set_title(title)

    if not legend_list:
        ax.legend(
            loc="best",
            prop={
                "size": "medium"
            }
        )
    else:
        ax.legend(
            legend_list,
            loc="best",
            prop={
                "size": "medium"
            }
        )
    # end of if/else legend entries

    add_footnote(fig)
    plt.tight_layout()

    if show_plot:
        plt.show()
    else:
        plt.plot()
# end of show_with_entities


def plot_overlay_pricing_and_volume(
        log_label,
        ticker,
        plot_colors,
        volume_color,
        df,
        show_plot=True):
    """plot_overlay_pricing_and_volume

    Plot pricing (high, low, open, close) and volume as
    an overlay off the x-axis

    :param log_label: log identifier
    :param ticker: ticker name
    :param plot_colors: colors to use
    :param volume_color: volume color
    :param df: pandas dataframe
    :param show_plot: bool to show the plot
    """

    rec = {
        'fig': None,
        'ax': None,
        'ax2': None
    }
    result = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)

    try:

        log.info(
            '{} - '
            'plot_overlay_pricing_and_volume'
            ' - start'.format(
                log_label))

        set_common_seaborn_fonts()

        fig, ax = plt.subplots(
            figsize=(15.0, 10.0))
        df[['date', 'close']].plot(
            x='date',
            linestyle='-',
            ax=ax,
            color=plot_colors[0])
        df[['date', 'high']].plot(
            x='date',
            linestyle='-',
            ax=ax,
            color=plot_colors[1])

        # use a second axis to display the
        # volume since it is in a different range
        # this will fill under the
        # volume's y values as well
        ax2 = ax.twinx()
        ax2.plot(
            df['date'],
            df['volume'],
            linestyle='-',
            color=volume_color,
            alpha=0.6)
        ax2.fill_between(
            df['date'].values,
            0,
            df['volume'].values,
            color=volume_color,
            alpha=0.5)
        # setup the second plot for volume
        ax2.set_ylim([0, ax2.get_ylim()[1] * 3])

        plt.grid(True)
        plt.xlabel('Dates')
        plt.ylabel('Prices')

        # Build a date vs Close DataFrame
        start_date = str(df.iloc[0]['date'].strftime('%Y-%m-%d'))
        end_date = str(df.iloc[-1]['date'].strftime('%Y-%m-%d'))
        use_title = (
            '{} Pricing from: {} to {}'.format(
                ticker,
                start_date,
                end_date))
        ax.set_title(use_title)

        # Merge in the second axis (volume) Legend
        handles, labels = plt.gca().get_legend_handles_labels()
        newLabels, newHandles = [], []
        for handle, label in zip(handles, labels):
            if label not in newLabels:
                newLabels.append(label)
                newHandles.append(handle)
        lines = ax.get_lines() + newHandles
        ax.legend(
            lines,
            [l.get_label() for l in lines],
            loc='best',
            shadow=True)

        # Build out the xtick chart by the dates
        ax.xaxis.grid(True, which='minor')
        xfmt = mdates.DateFormatter('%Y-%m-%d')
        ax.xaxis.set_major_formatter(xfmt)
        ax.xaxis.set_minor_formatter(xfmt)

        # turn off the grids on volume
        ax2.xaxis.grid(False)
        ax2.yaxis.grid(False)
        ax2.yaxis.set_ticklabels([])

        fig.autofmt_xdate()

        rec['fig'] = fig
        rec['ax'] = ax
        rec['ax2'] = ax2

        result = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        err = (
            'failed plot_overlay_pricing_and_volume '
            'and volume with ex={}'.format(
                e))
        result = build_result.build_result(
            status=ERR,
            err=err,
            rec=rec)
    # end of try/ex

    send_final_log(
        log_label=log_label,
        fn_name='plot_overlay_pricing_and_volume',
        result=result)

    return result
# end of plot_overlay_pricing_and_volume


def plot_hloc_pricing(
        log_label,
        ticker,
        df,
        title,
        show_plot=True):
    """plot_hloc_pricing

    Plot the high, low, open and close columns together on a chart

    :param log_label: log identifier
    :param ticker: ticker
    :param df: dataframe
    :param title: title for the chart
    :param show_plot: bool to show the plot
    """

    rec = {
        'ax': None,
        'fig': None
    }
    result = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)

    try:

        log.info(
            '{} - '
            'plot_hloc_pricing'
            ' - start'.format(
                log_label))

        set_common_seaborn_fonts()

        fig, ax = plt.subplots(
            figsize=(15.0, 10.0))

        plt.plot(
            df['date'],
            df['chigh'],
            label='High',
            color=PLOT_COLORS['high'],
            alpha=0.4)
        plt.plot(
            df['date'],
            df['clow'],
            label='Low',
            color=PLOT_COLORS['low'],
            alpha=0.4)
        plt.plot(
            df['date'],
            df['cclose'],
            label='Close',
            color=PLOT_COLORS['close'],
            alpha=0.4)
        plt.plot(
            df['date'],
            df['copen'],
            label='Open',
            color=PLOT_COLORS['open'],
            alpha=0.4)
        plt.plot(
            df['date'],
            df['fhigh'],
            label='Future High',
            color=PLOT_COLORS['high'])
        plt.plot(
            df['date'],
            df['flow'],
            label='Future Low',
            color=PLOT_COLORS['low'])
        plt.plot(
            df['date'],
            df['fclose'],
            label='Future Close',
            color=PLOT_COLORS['close'])
        plt.plot(
            df['date'],
            df['fopen'],
            label='Future Open',
            color=PLOT_COLORS['open'])

        xlabel = 'Dates'
        ylabel = 'Prices'

        plt.grid(True)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        # Build a date vs Close DataFrame
        start_date = str(df.iloc[0]['date'].strftime('%Y-%m-%d'))
        end_date = str(df.iloc[-1]['date'].strftime('%Y-%m-%d'))
        if not title:
            title = (
                '{} Pricing from: {} to {}'.format(
                    ticker,
                    start_date,
                    end_date))
        ax.set_title(title)

        # Build out the xtick chart by the dates
        ax.xaxis.grid(True, which='minor')

        legend_list = [
            'high',
            'low',
            'close',
            'open',
            'future high',
            'future low',
            'future close',
            'future low'
        ]

        fig.autofmt_xdate()
        show_with_entities(
            log_label=log_label,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            ax=ax,
            fig=fig,
            legend_list=legend_list,
            show_plot=show_plot)

        rec['ax'] = ax
        rec['fig'] = fig

        result = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        err = (
            'failed plot_hloc_pricing with ex={}'.format(
                e))
        log.error(err)
        result = build_result.build_result(
            status=ERR,
            err=err,
            rec=rec)
    # end of try/ex

    send_final_log(
        log_label=log_label,
        fn_name='plot_hloc_pricing',
        result=result)

    return result
# end of plot_hloc_pricing


def plot_df(
        log_label,
        title,
        column_list,
        df,
        xcol='date',
        xlabel='Date',
        ylabel='Pricing',
        linestyle='-',
        color='blue',
        show_plot=True):
    """plot_df

    :param log_label: log identifier
    :param title: title of the plot
    :param column_list: list of columns in the df to show
    :param df: dataframe
    :param xcol: x-axis column in the dataframe
    :param xlabel: x-axis label
    :param ylabel: y-axis label
    :param linestyle: style of the plot line
    :param color: color to use
    :param show_plot: bool to show the plot
    """

    rec = {
        'ax': None,
        'fig': None
    }
    result = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)

    try:

        log.info(
            '{} - '
            'plot_df'
            ' - start'.format(
                log_label))

        set_common_seaborn_fonts()

        hex_color = PLOT_COLORS['blue']
        fig, ax = plt.subplots(figsize=(15.0, 10.0))

        if linestyle == '-':
            df[column_list].plot(
                x=xcol,
                linestyle=linestyle,
                ax=ax,
                color=hex_color,
                rot=0)
        else:
            df[column_list].plot(
                kind='bar',
                x=xcol,
                ax=ax,
                color=hex_color,
                rot=0)

        if 'date' in str(xcol).lower():
            # plot the column
            min_date = df.iloc[0][xcol]
            max_date = df.iloc[-1][xcol]

            # give a bit of space at each end of the plot - aesthetics
            span = max_date - min_date
            extra = int(span.days * 0.03) * datetime.timedelta(days=1)
            ax.set_xlim([min_date - extra, max_date + extra])

            # format the x tick marks
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b\n%Y'))
            ax.xaxis.set_major_locator(plt.NullLocator())
            ax.xaxis.set_minor_locator(
                mdates.MonthLocator(
                    bymonthday=1,
                    interval=1))

            # grid, legend and yLabel
            ax.xaxis.grid(True, which='minor')

        # end of date formatting

        show_with_entities(
            log_label=log_label,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            ax=ax,
            fig=fig,
            show_plot=show_plot)

        rec['ax'] = ax
        rec['fig'] = fig

        result = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        err = (
            'failed plot_df title={} with ex={}'.format(
                title,
                e))
        result = build_result.build_result(
            status=ERR,
            err=err,
            rec=rec)
    # end of try/ex

    send_final_log(
        log_label=log_label,
        fn_name='plot_df',
        result=result)

    return result
# end of plot_df


def dist_plot(
        log_label,
        df,
        width=10.0,
        height=10.0,
        title='Distribution Plot',
        style='default',
        xlabel='',
        ylabel='',
        show_plot=True):
    """dist_plot

    Show a distribution plot for the passed in dataframe: ``df``

    :param log_label: log identifier
    :param df: pandas dataframe
    :param width: width of figure
    :param height: height of figure
    :param style: style to use
    :param xlabel: x-axis label
    :param ylabel: y-axis label
    :param show_plot: bool to show plot or not
    """

    rec = {}
    result = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)

    try:

        log.info(
            '{} - '
            'dist_plot'
            ' - start'.format(
                log_label))

        set_common_seaborn_fonts()

        fig, ax = plt.subplots(
            figsize=(width, height))

        if style == 'default':
            sns.set_context('poster')
            sns.axes_style('darkgrid')

        sns.distplot(
            df,
            color=PLOT_COLORS['blue'],
            ax=ax)

        if xlabel != '':
            ax.set_xlabel(xlabel)
        if ylabel != '':
            ax.set_ylabel(ylabel)

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        fig.suptitle(title)

        show_with_entities(
            log_label=log_label,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            ax=ax,
            fig=fig,
            show_plot=show_plot)

        rec['ax'] = ax
        rec['fig'] = fig

        result = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        err = (
            'failed dist_plot title={} with ex={}'.format(
                title,
                e))
        log.error(err)
        result = build_result.build_result(
            status=ERR,
            err=err,
            rec=rec)
    # end of try/ex

    send_final_log(
        log_label=log_label,
        fn_name='dist_plot',
        result=result)

    return result
# end of dist_plot
