function [tests, reject] = dm_boot(d, forecast_names);

B = 10000;
T = size(d,1);

wce_band = floor(T^(1/2));
wpe_band = floor(T^(1/3));

for j=1:size(d,2) % forecasts
    
    d_b = bootstrap(d(:,j),B,2*floor(T^(1/4)));
    d_bS = sort(mean(d_b));
    
    for bb=1:B+1
        
        if bb==1
            D = d(:,j);
            DD =  mean(D);
        else
            D = d_b(:,bb-1);
            DD = mean(D)- mean(d(:,j)); % centered mean for the bootstrap
            %Z(bb-1)=  mean(D);
        end
        
        WCEb = NeweyWest(D,wce_band,1);
                
        % DM using Weighted Covariance Estimate
        DM_WCEb(bb,j) = sqrt(T)* DD./ WCEb.^(0.5);
        
        % DM using Weighted Periodogram Estimate
        w= dftmtx(T)*D;
        pdm = w.* conj(w)/ (2*pi*T);
        WPE_b = sum(pdm(2:wpe_band+1,:))/wpe_band * 2*pi;
        DM_WPE_b(bb,j) = sqrt(T)* DD./ WPE_b.^(0.5);
        
        if bb==1
            SE = ([ WCEb WPE_b].^(0.5))/sqrt(T) ;
        end
        
    end
    
    %         tab(:,j)=[mean(d(:,j)) mean(Z) mean(Z)-mean(d(:,j)) ];
    %         tabt(:,j)=[median(DM_WCEb(2:end,j)) median(DM_WPE_b(2:end,j))];
    %
    tests(j,:) = [DM_WCEb(1,j) DM_WPE_b(1,j)];
    boot = [sort(abs(DM_WCEb(2:end,j))) sort(abs(DM_WPE_b(2:end,j)))];
    
    
    ind10b(j,:) = 10*(( abs(tests(j,:))> boot(B*0.90,:)) );
    ind5b(j,:) = 5*((abs(tests(j,:)) >  boot(B*0.95,:)) );
    
end
reject = ind10b'-ind5b';
%     printmat(tab,  'Mean(d)' , 'Data Boot Centered', '0 1 2 3 4');
%     printmat(tabt,  'Median(t_b)' , 'DM_WCEb DM_WPE_b', '0 1 2 3 4');
printmat(tests,  'Test' ,char(join(string(forecast_names))), 'DM_WCEb DM_WPE_b ' );
printmat(ind10b-ind5b, 'Bootstrap significance' ,  char(join(string(forecast_names))),'DM_WCEb DM_WPE_b');
disp('------------------------------------------------------------------------');
disp(' ');

