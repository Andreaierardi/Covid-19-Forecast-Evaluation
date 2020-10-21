clear, clc, close all
State = { 'US', 'California', 'Florida', 'New York', 'Texas'};
w0 = 5; % default 5
Loss = {'MSE', 'MAE', 'MAPE',  'LINEX'};

%% load realised data from github url
max_h = 4;
data_location = urlwrite("https://raw.githubusercontent.com/reichlab/covid19-forecast-hub/master/data-truth/truth-Cumulative%20Deaths.csv","dati.csv") ;
raw_data = readtable(data_location);
% raw_data = readtable('dati.csv');

%% section 3

for ss = 1 :5
    state = State{ss};
    temp = raw_data(strcmp(raw_data.location_name, state),[1 4]);
    dr = temp{:,2};
    date = datevec(datestr(temp{:,1},'yyyy-mm-dd'));
    
    % eliminate zeros
    date= date(dr>0,:);
    dr = dr(dr>0);
    
%     % select sample
%     sel_sample = [2020 8 30];
%     ind = find(datenum(date)<datenum(sel_sample));
%     date= date(ind,:);
%     disp(['Sample up to ', datestr(datenum(sel_sample-[0 0 1]))]);

    % aggregate to weekly (every Saturday)
    day = weekday(datenum(date));
    dr = dr(day==7);
    date = date(day==7,:);
    TT = timetable(datetime(date),dr);
    
    %% load the forecasts
    forecast_file = ['data_models-', state, '.xlsx'];
    [~,forecast_names]=xlsfinfo(forecast_file );
    
    forecast_names(9)=[];
    
    %% ------------------DONE-------------------------
    
    for k=1:numel(forecast_names)
        [forecast, info]=xlsread(forecast_file ,forecast_names{k});
        info(1,:)=[];
        for h=1:max_h
            ind = strcmp(info(:,3),[num2str(h),' wk ahead cum death']);
            temp1 = datenum(info(ind, 4),'dd-mmm-yy');
            temp = timetable(datetime(datestr(temp1)),forecast(ind,1));
            temp.Properties.VariableNames = {strcat(forecast_names{k},'_',num2str(h))};
            TT = synchronize(TT,temp);
            clear temp;
        end
    end
    date = datevec(TT.Time);
    
    %% benckmark quadratic model
    for h=1:max_h
        w = w0; %+2*h;
        bench(1:size(date,1),1)=NaN;
        for t = 1: length(dr)+1-w
            fhat = fit((t:t+w-1)', dr(t:t+w-1), 'poly2');
            bench(t+w-1+h,1) = max([dr(t+w-1) fhat(t+w-1+h)]);
        end
        temp = timetable(datetime(date), bench(1:size(date,1)));
        temp.Properties.VariableNames = {strcat('q_',num2str(h))};
        TT = synchronize(TT,temp);
        clear temp
    end
    
    clear bench dr date day fhat forecast gof h ind info k t temp1
    
    % disp('Up to 18 July');
    % TT = TT(1:20,:);
    
    date = datevec(TT.Time);
    data_all = TT{:,:};
    data = data_all(:,1);
    data_all(:,1) = [];
    for h=1:max_h
        forecasts(:,:,h) = data_all(:,h:max_h:end);
    end
    
    %% plot
    if ss==1
    tt =datenum(date);
    figure
    for h=1:max_h
%         if h==1||h==3
%             fig = figure
%         end
%         if h==1||h==2
%             subplot(2,1,h)
%         else
%             subplot(2,1,h-2)
%         end
subplot(2,2,h)
        ind = sum(isnan([data forecasts(:,:,h)]),2)==0;
        aa = find(ind==1,1, 'first'): find(ind==1,1, 'last');
        plot(tt(aa),data(aa),'.b','MarkerSize', 15);
        hold on;
        plot(tt(aa),forecasts(aa,1,h),'k','Linewidth', 2);
        plot(tt(aa),forecasts(aa,2:end-1,h));
        plot(tt(aa),forecasts(aa,end,h),'--r','Linewidth', 1.5);
        plot(tt(aa),data(aa),'.b','MarkerSize', 15);
        at = [state,', h=', num2str(h)];
        title(at);
        datetick('x','dd-mm');
        axis tight;
        grid on;
        hold off
%         if h==2||h==4
            if h==4
            legend1 = legend(['Data',forecast_names, {'Polyn'}], 'location',...
                'best','Linewidth', 1,'Autoupdate','off','FontSize',7);
     set(legend1, 'Position',[0.130641745989977 0.0302050091835305 0.768359365162905 0.031967212357482],...
     'Orientation','horizontal',...
    'LineWidth',1.5,...
    'AutoUpdate','off','NumColumns',6);

            print('-bestfit',['./results/', at],'-dpdf');
        end  
        e = data(aa)-forecasts(aa,:,h);
        
        
        tab = [mean(e); median(e); std(e); max(e); min(e); skewness(e); ...
            diag(corr(e(2:end,:),e(1:end-1,:)))'; diag(corr(e(3:end,:),e(1:end-2,:)))'];
        
        printmat(tab', [num2str(h),'-steps'],[char(join(string(forecast_names))), ' Polyn'] ,...
            'Mean Median Std Max Min Skew AR1 AR2');
        
    end
    end
    
    %% forecast evaluation
    
    disp(['----------- ', state,' ------------'] );
    for ll=1:4
        loss = Loss{ll};
        if strcmp(loss,'LINEX')
            a = 0.50;
            disp(['------------- Linex Loss, a=', num2str(a),' --------------']);
        else
            disp(['----------- ', loss,' ------------']);
        end
        
        for h=1:max_h
            ind = sum(isnan([data forecasts(:,:,h)]),2)==0;
            e = data(ind,:)-forecasts(ind,:,h);            
            if strcmp(loss,'MSE')
                L = e.^2;
            elseif strcmp(loss,'MAPE')
                L = abs(e)./ data(ind,:);
            elseif strcmp(loss,'MAE')
                L = abs(e);
            elseif strcmp(loss,'LINEX')
                L = exp(a*100*e./ data(ind,:)) - a*100*e./ data(ind,:) -1 ;
            end
            d = L(:,end)-L(:,1:end-1);
            for k = 1 : numel(forecast_names)
                [test(:,k,h,ll), cv(:,:,h), reject(:,k,h,ll)] = dm_fsa_cv(d(:,k));
            end
            aa =date(ind,:);
            tit = [num2str(h),'-steps: test statistics, ', datestr(aa(1,:)),' - ', datestr(aa(end,:)),', N=',num2str(sum(ind)) ];
            if ss==1&& ll==1
                disp(tit);
                [test_b, rejectb] = dm_boot(d, forecast_names);
            else
                printmat(test(:,:,h,ll)', tit,  char(join(string(forecast_names))),'Fixed-b fixed-m');
            end
            printmat(reject(:,:,h,ll)',  'Fixed-b fixed-m', char(join(string(forecast_names))),[num2str(h),'-steps: fsa significance']);
        end
    end
    
    %% Figures
    markerlist = {'+';'d';'*';'o'};
    aa= char(forecast_names);
    
    for fix =1:2
        figure
        for h=1:4
            subplot(2,2,h)
            for ll=1:4
                plot(test(fix,:,h,ll), markerlist{ll},'MarkerSize',5,'LineWidth',2); hold on
            end
            if h==3
                legend1 = legend('MSE','MAE', 'MAPE', 'LINEX','AutoUpdate','off','Orientation','horizontal');
                set(legend1, 'Position',[0.379753567319073 0.0148553599940293 0.254296872171108 0.031967212357482]);
            end
            plot(0:numel(forecast_names)+1,zeros(numel(forecast_names)+2,1),'k');
            hold on
            plot(0:numel(forecast_names)+1, kron([-cv(fix,1,h) cv(fix,1,h)],ones(numel(forecast_names)+2,1)),':r');
            hold on
            plot(0:numel(forecast_names)+1, kron([-cv(fix,2,h) cv(fix,2,h)],ones(numel(forecast_names)+2,1)),'--r');
            hold on
            plot(0:numel(forecast_names)+1, kron([-cv(fix,3,h) cv(fix,3,h)],ones(numel(forecast_names)+2,1)),'-r');
            xlim([0 numel(forecast_names)+1]);
            
            if fix==1
                title([state,', h=',num2str(h), ', WCE']);              
            else
                title([state,', h=',num2str(h), ', WPE']);
            end
            xticks(1:numel(forecast_names));
            xticklabels(aa(:,1:2));
        end
        if fix==1
            print('-bestfit',['./results/',state(1:2),'_wce'],'-dpdf');            
        else
            print('-bestfit',['./results/',state(1:2),'_wpe'],'-dpdf');
        end
        
    end
    
    %% plots for US   
    if ss ==1
        figure
        subplot(3,1,1)
        plot(datenum(date(ind,:)), [forecasts(ind,[1 end],4) data(ind)]);
        xlim([min(datenum(date(ind,:))) max(datenum(date(ind,:)))]);
        legend('Ensamble','Quadratic','Data', 'Location','best');
        datetick('x','dd-mm');
        
        subplot(3,1,2)
        plot(datenum(date(ind,:)), (forecasts(ind,[1 end],4)-data(ind)).^2);
        xlim([min(datenum(date(ind,:))) max(datenum(date(ind,:)))]);
        legend('Ensamble','Quadratic','Location','best');
        datetick('x','dd-mm');
        title('Quadratic Loss');
        
        e = (data(ind)-forecasts(ind,[1 end],4))./data(ind);
        a = 30;
        L = exp(a*e) - a*e -1 ;
        subplot(3,1,3)
        plot(datenum(date(ind,:)), L);
        xlim([min(datenum(date(ind,:))) max(datenum(date(ind,:)))]);
        legend('Ensamble','Quadratic','Location','best');
        datetick('x','dd-mm');
        title('Linex Loss');
        
        
    end
    clear forecasts;
end

%% plot loss functions
ee = -100:2:100;
a = 0.5;
figure
plot(ee, [ ee.^2; abs(ee); exp(a*ee)-a*ee-1]'); ylim([0 100]);