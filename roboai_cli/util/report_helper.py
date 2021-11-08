import json
import pandas as pd
# pd.set_option('display.max_rows', 2000) 
import numpy as np
from sklearn.model_selection import train_test_split
import math
from os import listdir
from os.path import isfile, join
from unidecode import unidecode

from os.path import abspath, join, exists
from roboai_cli.util.cli import loading_indicator, print_info, print_message, print_error, print_success

class Report:

    """"""

    def __init__(
        self,
        file: tuple,
        file_format: str, 
        nlu_threshold: float, 
        ambiguity_threshold: float, 
        output_name: str
    ) -> None:
        """Initializes the Report object.
        """

        if not exists(file):
            print_message('Conversation file not found')
            exit(0)

        possible_file_formats = { 
            "roboai_csv" : self.__importer_roboai_csv_bug_2_1, 
            "roboai_xlsx" : self.__todo,
        }
        if file_format in possible_file_formats:

            self.__file = file
            self.__file_format = file_format
            self.__nlu_threshold = nlu_threshold
            self.__ambiguity_threshold = ambiguity_threshold
            self.__output_name = output_name

            possible_file_formats[file_format]()

        else:
            print_message('File type not supported at the time')
            exit(0)



    def run(self):
        self.__conversational_kpi()
        self.__conversational_kpi_output()
        print_success("The end")



    def __todo(_):
        print_message('File type not supported at the time')
        exit(0)


    """
    columns: conversation_id timestamp message intent_1 confidence_1 intent_2 confidence_2 intent_3 confidence_3 (answers entities)
    'conversation_id', 'timestamp', 'message', 'intent_1', 'confidence_1', 'intent_2', 'confidence_2', 'intent_3', 'confidence_3', 'answers', 'entities'
    """

    def __importer_roboai_csv_bug_2_1(self):
        pd_data = pd.read_csv(self.__file)
        pd_data = pd_data[["dialogue_uuid", "timestamp", "message", "intent_identifier1", "intent_confidence1", "intent_identifier2", "intent_confidence2", "intent_identifier3", "intent_confidence3",	"answers", "entities"]]
        pd_data.rename(columns={
            "dialogue_uuid":"conversation_id",
            "intent_identifier1":"intent_2",
            "intent_confidence1":"confidence_2",
            "intent_identifier2":"intent_1",
            "intent_confidence2":"confidence_1",
            "intent_identifier3":"intent_3",
            "intent_confidence3":"confidence_3",
            }, inplace=True)
        self.__pd_data_og = pd_data.copy()

    def __conversational_kpi(self):
        self.__pd_data = self.__pd_data_og.copy()

        period_analysed = self.__pd_data['timestamp'].unique()
        print_message(f"From Date: {str(period_analysed.min())}")
        print_message(f"End Date: {str(period_analysed.max())}")
        period_analysed = f"{str(period_analysed.min())[:10]} -> {str(period_analysed.max())[:10]}"
        print_message(period_analysed)

        number_inputs,_ = self.__pd_data.shape
        print_message(f"Number of Raw inputs:  {number_inputs}")

        count_conversations = pd.DataFrame(self.__pd_data['conversation_id'].value_counts()).reset_index()
        count_conversations.rename(columns={'index': 'conversation_id', 'conversation_id': 'count'}, inplace=True)
        self.__count_conversations = count_conversations[['count', 'conversation_id']]

        self.__number_conversations,_ = count_conversations.shape
        print_message(f"Number of conversations:  {self.__number_conversations}")

        avg_steps = count_conversations["count"].mean()
        print_message(f"Average number of steps in conversation:  {avg_steps}")

        max_steps = count_conversations["count"].max()
        print_message(f"Maximum number of steps in conversation:  {max_steps}")

        min_steps = count_conversations["count"].min()
        print_message(f"Minimum number of steps in conversation:  {min_steps}")

        empty_lines = self.__pd_data[pd.isna(self.__pd_data['message'])].index
        number_empty_lines = len(empty_lines)
        print_message(f"Number of empty lines:  {number_empty_lines}")
        self.__pd_data = self.__pd_data.drop(empty_lines)

        self.__pd_data['is_email'] = np.where(self.__pd_data["message"].str.match("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"), True, False)
        number_is_email = self.__pd_data['is_email'].value_counts()
        if True in number_is_email:
            self.__number_is_email = number_is_email.at[True]
            print_message(f"Number of msg that only contain emails:  {self.__number_is_email}")
            self.__pd_is_email = self.__pd_data[self.__pd_data['is_email']]
            self.__pd_is_email = self.__pd_is_email[['conversation_id', 'timestamp', 'message']]
            self.__pd_data = self.__pd_data[~self.__pd_data['is_email']]
        else:
            self.__number_is_email = 0
            self.__pd_is_email = pd.DataFrame(columns=['conversation_id', 'timestamp', 'message'])
            print_success(f"Number of msg that only contain emails:  {self.__number_is_email}")

        self.__pd_data['is_n_alpha'] = np.where(self.__pd_data["message"].str.match("^((?![A-Za-z]).)*$"), True, False)
        number_is_n_alpha = self.__pd_data['is_n_alpha'].value_counts()
        if True in number_is_n_alpha:
            self.__number_is_n_alpha = number_is_n_alpha.at[True]
            print_message(f"Number of msg that do not contain letters:  {self.__number_is_n_alpha}")
            self.__pd_is_n_alpha = self.__pd_data[self.__pd_data['is_n_alpha']]
            self.__pd_is_n_alpha = self.__pd_is_n_alpha[['conversation_id', 'timestamp', 'message']]
            self.__pd_data = self.__pd_data[~self.__pd_data['is_n_alpha']]
        else:
            self.__number_is_n_alpha = 0
            self.__pd_is_n_alpha = pd.DataFrame(columns=['conversation_id', 'timestamp', 'message'])
            print_success(f"Number of msg that do not contain letters:  {self.__number_is_n_alpha}")

        self.__pd_data['is_outofscale'] = np.where(np.logical_or(0 > self.__pd_data["confidence_1"], self.__pd_data["confidence_1"] > 1), True, False)
        number_is_outofscale = self.__pd_data['is_outofscale'].value_counts()
        if True in number_is_outofscale:
            self.__number_is_outofscale = number_is_outofscale.at[True]
            print_error(f"Number of msg that the Confidence 1 exceeds limits:  {self.__number_is_outofscale}")
            self.__pd_is_outofscale = self.__pd_data[self.__pd_data['is_outofscale']]
            self.__pd_is_outofscale = self.__pd_is_outofscale[['conversation_id', 'timestamp', 'message', 'intent_1', 'confidence_1']]
            self.__pd_data = self.__pd_data[~self.__pd_data['is_n_alpha']]
        else:
            self.__number_is_outofscale = 0
            self.__pd_is_outofscale = pd.DataFrame(columns=['conversation_id', 'timestamp', 'message', 'intent_1', 'confidence_1'])
            print_success(f"Number of msg that the Confidence 1 exceeds limits:  {self.__number_is_outofscale}")

        count_confidence = len(self.__pd_data["confidence_1"])
        print_message(f"Number of refined inputs:  {count_confidence}")

        avg_confidence = self.__pd_data["confidence_1"].mean()
        print_info(f"Average confidence:  {avg_confidence}")

        max_confidence = self.__pd_data["confidence_1"].max()
        print_message(f"Maximum confidence:  {max_confidence}")

        min_confidence = self.__pd_data["confidence_1"].min()
        print_message(f"Minimum confidence:  {min_confidence}")

        self.__pd_data['not_confident'] = np.where(self.__pd_data["confidence_1"] < self.__nlu_threshold , True, False)
        number_not_confident = self.__pd_data['not_confident'].value_counts()
        if True in number_not_confident:
            self.__number_not_confident = number_not_confident.at[True]
            print_info(f"Number of inputs without enough confidence:  {self.__number_not_confident}")
            self.__pd_not_confident = self.__pd_data[self.__pd_data['not_confident']]
            self.__pd_not_confident = self.__pd_not_confident[['conversation_id', 'timestamp', 'intent_1', 'confidence_1', 'intent_2', 'confidence_2', 'intent_3', 'confidence_3', 'message', 'entities']].sort_values('message', ascending=True)
            self.__pd_data = self.__pd_data[~self.__pd_data['not_confident']]
        else:
            self.__number_not_confident = 0
            self.__pd_not_confident = pd.DataFrame(columns=['conversation_id', 'timestamp', 'message', 'intent_1', 'confidence_1', 'intent_2', 'confidence_2', 'intent_3', 'confidence_3', 'entities'])
            print_success(f"Number of inputs without enough confidence:  {self.__number_not_confident}")

        self.__pd_data['val_ambiguous'] = self.__pd_data["confidence_1"] - self.__pd_data["confidence_2"]
        self.__pd_data['ambiguous'] = np.where(self.__pd_data['val_ambiguous'] <= self.__ambiguity_threshold, True, False)
        number_ambiguous = self.__pd_data['ambiguous'].value_counts()
        if True in number_ambiguous:
            self.__number_ambiguous = number_ambiguous.at[True]
            print_message(f"Number of inputs with ambiguous confidence:  {self.__number_ambiguous}")
            self.__pd_ambiguous = self.__pd_data[self.__pd_data['ambiguous']]
            self.__pd_ambiguous = self.__pd_ambiguous[['conversation_id', 'timestamp', 'intent_1', 'confidence_1', 'intent_2', 'confidence_2', 'message', 'val_ambiguous']].sort_values('val_ambiguous', ascending=True)
            self.__pd_data = self.__pd_data[~self.__pd_data['ambiguous']]
        else:
            self.__number_ambiguous = 0
            self.__pd_ambiguous = pd.DataFrame(columns=['conversation_id', 'timestamp', 'message', 'intent_1', 'confidence_1', 'intent_2', 'confidence_2', 'val_ambiguous'])
            print_success(f"Number of inputs with ambiguous confidence:  {self.__number_ambiguous}")

        self.__pd_data = self.__pd_data[['conversation_id', 'timestamp', 'message', 'answers', 'intent_1', 'confidence_1', 'intent_2', 'confidence_2', 'intent_3', 'confidence_3', 'entities']]
        self.__successfully_answered,_ = self.__pd_data.shape

        self.__freq_intent = pd.DataFrame(self.__pd_data['intent_1'].value_counts())
        self.__freq_intent.rename(columns={'intent_1': 'Intent Count'}, inplace=True)

        self.__pd_info = pd.DataFrame([
            ["Logs",""],
            ["Period of analysed logs", period_analysed],
            ["Number of inputs", number_inputs],
            ["Number of empty lines extracted", number_empty_lines],
            ["Number of msg that only contain emails", self.__number_is_email],
            ["Number of msg that do not contain letters", self.__number_is_n_alpha],
            ["Number of Intent confidence > 1 extracted", self.__number_is_outofscale],
            # ["Number of duplicate entries", number_count_duplicates],
            ["Number of conversations", self.__number_conversations],
            ["Avg. number of steps per conversation", avg_steps],
            ["Max. number of steps per conversation", max_steps],
            ["Min. number of steps per conversation", min_steps],
            ["Number of refined inputs", count_confidence],
            ["Average confidence", avg_confidence],
            ["Max. confidence", max_confidence],
            ["Min. confidence", min_confidence],
            ["Number of successfully answered questions", self.__successfully_answered],
            # ["Number of successfully answered questions (No duplicates)", len_count_duplicates_final],
            ["Number of ambiguous inputs", self.__number_ambiguous],
            ["Number of unanswered questions", self.__number_not_confident],
            # ["Number of duplicates in unanswered questions", number_count_duplicates]
        ])

    def __conversational_kpi_output(self):
        len_pd_info, _  = self.__pd_info.shape
        len_freq_intent, _ = self.__freq_intent.shape

        with pd.ExcelWriter(self.__output_name, engine="xlsxwriter") as xlsx_writer:
            
            workbook = xlsx_writer.book
            
            new_worksheet_1 = workbook.add_worksheet("Info")
            new_worksheet_2 = workbook.add_worksheet("Low Confidence")
            new_worksheet_3 = workbook.add_worksheet("Ambiguous")
            # new_worksheet_4 = workbook.add_worksheet("Duplicate entries")
            new_worksheet_5 = workbook.add_worksheet("Correctly Predicted")
            new_worksheet_6 = workbook.add_worksheet("Emails, Not Alpha and OO-Scale")
            
            xlsx_writer.sheets["Info"] = new_worksheet_1
            xlsx_writer.sheets["Low Confidence"] = new_worksheet_2
            xlsx_writer.sheets["Ambiguous"] = new_worksheet_3
            # xlsx_writer.sheets["Duplicate entries"] = new_worksheet_4
            xlsx_writer.sheets["Correctly Predicted"] = new_worksheet_5
            xlsx_writer.sheets["Emails, Not Alpha and OO-Scale"] = new_worksheet_6
            
            new_worksheet_1.set_column(0, 0, 55)
            new_worksheet_1.set_column(1, 1, 24)
            
            self.__pd_info.to_excel(xlsx_writer, sheet_name="Info", startrow=0, startcol=0, index=False, header=False)
            new_worksheet_1.add_table(0, 0, (len_pd_info - 1), 1, {'columns': [{'header': "Logs"},{'header': " "}]})
            
            self.__freq_intent.to_excel(xlsx_writer, sheet_name="Info", startrow=(len_pd_info + 3), startcol=0, index=True, header=True)
            new_worksheet_1.add_table((len_pd_info + 3), 0, ((len_pd_info + 3) + len_freq_intent), 1, {'columns': [{'header': " "},{'header': "Intent Count"}]})
            
            self.__count_conversations.to_excel(xlsx_writer, sheet_name="Info", startrow=(len_pd_info + 3), startcol = 4, index=False, header=True)
            new_worksheet_1.add_table((len_pd_info + 3), 4, ((len_pd_info + 3) + self.__number_conversations), 5, {'columns': [{'header': "Steps"},{'header': "ConversationId"}]})
            new_worksheet_1.set_column(4, 4, 24)
            new_worksheet_1.set_column(5, 5, 200)
            
            self.__pd_not_confident.to_excel(xlsx_writer, sheet_name="Low Confidence", startrow=0, startcol = 0, index=False, header=True)
            new_worksheet_2.add_table(0, 0, (self.__number_not_confident if self.__number_not_confident > 0 else 1), 8, {'columns': [{'header': "ConversationId"}, {'header': "TimeStamp"}, {'header': "Intent 1"}, {'header': "Confidence 1"}, {'header': "Intent 2"}, {'header': "Confidence 2"}, {'header': "Intent 3"}, {'header': "Confidence 3"}, {'header': "User Message"}, {'header': "Entities"}]})
            new_worksheet_2.set_column(0, 0, 35, None, {'hidden': 1})
            new_worksheet_2.set_column(1, 1, 25, None, {'hidden': 1})
            for i in [2,4,6,9]:
                new_worksheet_2.set_column(i, i, 25)
            for i in [3,5,7]:
                new_worksheet_2.set_column(i, i, 10)
            new_worksheet_2.set_column(8, 8, 90)
                
            self.__pd_ambiguous.to_excel(xlsx_writer, sheet_name="Ambiguous", startrow=0, startcol=0, index=False, header=True)
            new_worksheet_3.add_table(0, 0, (self.__number_ambiguous if self.__number_ambiguous > 0 else 1), 7, {'columns': [{'header': "ConversationId"}, {'header': "TimeStamp"}, {'header': "Intent 1"}, {'header': "Confidence 1"}, {'header': "Intent 2"}, {'header': "Confidence 2"}, {'header': "User Message"}, {'header': "Ambiguity"}]})
            new_worksheet_3.set_column(0, 0, 35, None, {'hidden': 1})
            new_worksheet_3.set_column(1, 1, 25, None, {'hidden': 1})
            for i in [2,4]:
                new_worksheet_3.set_column(i, i, 25)
            for i in [3,5,7]:
                new_worksheet_3.set_column(i, i, 10)
            new_worksheet_3.set_column(6, 6, 90)
                
            # self.__pd_count_duplicates.to_excel(xlsx_writer, sheet_name="Duplicate entries", startrow=0, startcol=0, index=False, header=True)
            # new_worksheet_4.add_table(0, 0, len_count_duplicates, 1, {'columns': [{'header': "User query"}, {'header': "Number of Duplicates"}]})
            # new_worksheet_4.set_column(0, 0, 90)
            # new_worksheet_4.set_column(1, 1, 25)
            
            self.__pd_data.to_excel(xlsx_writer, sheet_name="Correctly Predicted", startrow=0, startcol=0, index=False, header=True)
            new_worksheet_5.add_table(0, 0, self.__successfully_answered, 10, {'columns': [{'header': "ConversationId"}, {'header': "TimeStamp"},  {'header': "User Message"}, {'header': "Bot Message"}, {'header': "Intent 1"}, {'header': "Confidence 1"}, {'header': "Intent 2"}, {'header': "Confidence 2"}, {'header': "Intent 3"}, {'header': "Confidence 3"}, {'header': "Entities"}]})
            new_worksheet_5.set_column(0, 0, 35, None, {'hidden': 1}) #'conversation_id'
            new_worksheet_5.set_column(1, 1, 25, None, {'hidden': 1}) #'timestamp'
            new_worksheet_5.set_column(2, 2, 90) #'message'
            new_worksheet_5.set_column(3, 3, 90) #'answers'
            new_worksheet_5.set_column(4, 4, 25) #'intent_1'
            new_worksheet_5.set_column(5, 5, 10) #'confidence_1'
            for i in [6,8,10]: #'intent_2' 6,  'intent_3' 8,  'entities' 10
                new_worksheet_5.set_column(i, i, 25, None, {'hidden': 1})
            for i in [7,9]: #'confidence_2' 7,'confidence_3' 9,
                new_worksheet_5.set_column(i, i, 10, None, {'hidden': 1})
            
            
            # pd_count_duplicates_final.to_excel(xlsx_writer, sheet_name="Correctly Predicted", startrow=0, startcol=6, index=False, header=True)
            # new_worksheet_5.add_table(0, 6, len_count_duplicates_final, 7, {'columns': [{'header': "User query"}, {'header': "Number of Duplicates"}]})
            # new_worksheet_5.set_column(6, 6, 60)
            # new_worksheet_5.set_column(7, 7, 25)
            
            self.__pd_is_email.to_excel(xlsx_writer, sheet_name="Emails, Not Alpha and OO-Scale", startrow=0, startcol=0, index=False, header=True)
            self.__pd_is_n_alpha.to_excel(xlsx_writer, sheet_name="Emails, Not Alpha and OO-Scale", startrow=0, startcol=5, index=False, header=True)
            self.__pd_is_outofscale.to_excel(xlsx_writer, sheet_name="Emails, Not Alpha and OO-Scale", startrow=0, startcol=10, index=False, header=True)
            new_worksheet_6.add_table(0, 0, (self.__number_is_email if self.__number_is_email > 0 else 1), 2, {'columns': [{'header': "ConversationId"}, {'header': "TimeStamp"}, {'header': "Emails"}]})
            new_worksheet_6.add_table(0, 5, (self.__number_is_n_alpha if self.__number_is_n_alpha > 0 else 1), 7, {'columns': [{'header': "ConversationId"}, {'header': "TimeStamp"}, {'header': "Non Alpha Messages"}]})
            new_worksheet_6.add_table(0, 10, (self.__number_is_outofscale if self.__number_is_outofscale > 0 else 1), 14, {'columns': [{'header': "ConversationId"}, {'header': "TimeStamp"}, {'header': "User Message"}, {'header': "Intent 1"}, {'header': "(Out-of-scale) Confidence 1"}]})
            for i in [0,1,5,6]:
                new_worksheet_6.set_column(i, i, 25, None, {'hidden': 1})
            for i in [2,7,10,11,12,13,14]:
                new_worksheet_6.set_column(i, i, 35)